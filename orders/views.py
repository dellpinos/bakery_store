import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Cart, CartProduct, Order, OrderProduct
from products.models import Product, Category
from users.models import Notification
from .utils import generate_unique_token

from dashboard.views import check_dates

# Checkout view
@login_required
def checkout(request):

    # Validation
    try:
        cart = request.user.cart.get()

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    cart_products = cart.products.all()
    products = []
    seller_user = None
    total_cart_quantity = 0
    min_day = 0 # the longest production time in the current order

    for cart_prod in cart_products:

        prod = cart_prod.product
        ingredients = prod.ingredients.filter(deleted_at = None)
        prod.total_price = float(prod.subtotal_price)
        prod.quantity = cart_prod.quantity
        seller_user = prod.seller_user
        total_cart_quantity += cart_prod.quantity

        # Calculates first possible delivery date
        if prod.production_time > min_day:
            min_day = prod.production_time

        # Calculates total price
        for productIngredient in ingredients:
            prod.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

        products.append(prod)

    if not seller_user or total_cart_quantity == 0 :
        return HttpResponseRedirect(reverse('index'))

    # Calculates min date (with production time)
    today = datetime.now()
    time_zone_correction = min_day + 1 # NOTE: The production time calculation does not include the current day
    min_date_formatted = (today + timedelta(days=time_zone_correction))

    # Look for seller days off
    disabled_days = list(seller_user.days_off.values_list('date', flat = True))

    # Look for all orders
    prev_orders = Order.objects.filter(seller_user = seller_user, deleted_at = None, archived = False)

    max_prod_per_day = seller_user.max_prod_capacity

    # # Calculates total quantities
    order_products_summary = []

    for order in prev_orders:
        # Sum all the products from each order
        total_quantity = order.products.aggregate(total = Sum('quantity'))
        total_quantity = total_quantity['total'] or 0 # Assign 0 instead of None

        order_products_summary.append({
            'order_id': order.id,
            'total_products': total_quantity,
            'date' : order.delivery_date
        })

    # Groups orders by date with total quantity
    grouped_by_date = {}
    
    # Iterates the list to obtain a dictionary of dates with their quantities
    for entry in order_products_summary:
        date = entry['date']

        # If it doesn't exist, it assigns a value of 0 to accumulate later
        if date not in grouped_by_date:
            grouped_by_date[date] = 0

        # If it exists, it adds its value to 'total_products'
        grouped_by_date[date] += entry['total_products']

    # Convert the dictionary into a list of dictionaries
    result_summary = [{'date': date, 'total_products': total} for date, total in grouped_by_date.items()]

    # Adds the dates where the quantity received in this request exceeds the maximum products per day
    for summary in result_summary:
        if ( summary['total_products'] + total_cart_quantity ) > max_prod_per_day:
            disabled_days.append(summary['date'])

    # Removes any duplicates
    disabled_days = list(set(disabled_days))

    # ISO Format
    disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]

    categories = Category.objects.all()

    return render(request, 'orders/checkout.html', {
        "products" : products,
        "seller_user" : seller_user,
        "disabled_days" : json.dumps(disabled_days_list),
        "min_day": min_date_formatted.strftime("%Y-%m-%d"),
        "min_day_number": min_day,
        "categories": categories
    })

# Pending Orders view (seller)
@login_required
def pending_orders(request):
    
    orders = Order.objects.filter(seller_user = request.user, deleted_at = None, archived = False).order_by('delivery_date')

    for order in orders:
        order_products = order.products.filter(deleted_at = None)
        order.products_list = []
        order.total_products = 0
        order.delivery_date_formated = order.delivery_date.strftime('%m/%d/%Y')
        order.purchance_date_formated = order.created_at.strftime('%m/%d/%Y %H:%M hs')

        for prod in order_products:
            order.total_products += prod.quantity
            order.products_list.append(
                {
                    "name" : prod.product.name,
                    "quantity" : prod.quantity,
                    "id" : prod.product.id
                }
            )

    # Paginator
    p = Paginator(orders, 5) # NOTE: Items per page

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, 'orders/pendings.html', {
        "page": page
    })

# Archived Orders view (seller)
@login_required
def archived_orders(request):
    
    orders = Order.objects.filter(seller_user = request.user, deleted_at = None, archived = True).order_by('-created_at')

    for order in orders:
        order_products = order.products.filter(deleted_at = None)
        order.products_list = []
        order.total_products = 0
        order.delivery_date_formated = order.delivery_date.strftime('%m/%d/%Y')
        order.purchance_date_formated = order.created_at.strftime('%m/%d/%Y %H:%M hs')

        for prod in order_products:
            order.total_products += prod.quantity
            order.products_list.append(
                {
                    "name" : prod.product.name,
                    "quantity" : prod.quantity,
                    "id" : prod.product.id
                }
            )

    # Paginator
    p = Paginator(orders, 5) # NOTE: Items per page

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    categories = Category.objects.all()

    return render(request, 'orders/archived.html', {
        "page": page,
        "categories": categories
    })

# Pending Orders view (buyer)
@login_required
def pending_deliveries(request):

    orders = Order.objects.filter(buyer_user = request.user, deleted_at = None, archived = False).order_by('delivery_date')

    for order in orders:
        order_products = order.products.filter(deleted_at = None)
        order.products_list = []
        order.total_products = 0
        order.delivery_date_formated = order.delivery_date.strftime('%m/%d/%Y')
        order.purchance_date_formated = order.created_at.strftime('%m/%d/%Y %H:%M hs')

        for prod in order_products:
            order.total_products += prod.quantity
            order.products_list.append(
                {
                    "name" : prod.product.name,
                    "quantity" : prod.quantity,
                    "id" : prod.product.id
                }
            )

    # Paginator
    p = Paginator(orders, 5) # NOTE: Items per page

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    categories = Category.objects.all()

    return render(request, 'orders/pending_deliveries.html', {
        "page": page,
        "categories": categories
    })

# Archived Orders view (buyer)
@login_required
def archived_deliveries(request):

    orders = Order.objects.filter(buyer_user = request.user, deleted_at = None, archived = True).order_by('-created_at')

    for order in orders:
        order_products = order.products.filter(deleted_at = None)
        order.products_list = []
        order.total_products = 0
        order.delivery_date_formated = order.delivery_date.strftime('%m/%d/%Y')
        order.purchance_date_formated = order.created_at.strftime('%m/%d/%Y %H:%M hs')

        for prod in order_products:
            order.total_products += prod.quantity
            order.products_list.append(
                {
                    "name" : prod.product.name,
                    "quantity" : prod.quantity,
                    "id" : prod.product.id
                }
            )

    # Paginator
    p = Paginator(orders, 5) # NOTE: Items per page

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    categories = Category.objects.all()

    return render(request, 'orders/archived_deliveries.html', {
        "page": page,
        "categories": categories
    })


## API ##

# Get user's cart
@login_required
def index_cart(request):

    cart = Cart.objects.filter(user=request.user).first()

    if cart is None:
        return JsonResponse({
            "msg" : "There is no products in the cart",
            "response" : 0
            }, status = 200
        )

    products_count = cart.products.count()

    if products_count > 0:
        cart_products = cart.products.all()
        serialized_products = []

        # Calculates total price
        for cart_product in cart_products:
            product = cart_product.product
            ingredients = product.ingredients.filter(deleted_at = None)

            if not ingredients:
                return JsonResponse({
                    "msg" : "Corrumpted record (product)",
                    "response" : 0
                    }, status = 422
                )
            
            product.total_price = float(product.subtotal_price)

            for productIngredient in ingredients:
                product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

            serialized_product = {
                "id" : product.id,
                "image" : product.image,
                "price" : product.total_price,
                "production_time" : product.production_time,
                "name" : product.name,
                "seller" : product.seller_user.username
            }

            serialized_products.append(serialized_product)

        return JsonResponse({
            "response" : products_count,
            "products" : serialized_products
        }, status = 200)

    else:
        return JsonResponse({
            "msg" : "There is no products in the cart",
            "response" : 0
            }, status = 200
        )

# Add new product and create user's cart
@login_required
def create_cart(request, product):

    product_db = Product.objects.filter(pk=product, deleted_at = None).first()

    if product_db is None:
        return JsonResponse(
            {"error" : "Forbidden"}, status = 403
        )
    
    cart = Cart.objects.filter(user=request.user).first()

    # Create Cart if doesn't exist
    if cart is None:
        cart = Cart(
            user = request.user
        )
        cart.save()

    for prod in cart.products.all():
        if prod.product.id == product_db.id:
            return JsonResponse(
                {"error" : "Product already in cart"}, status=403
            )
        
    max_prod_capacity = product_db.seller_user.max_prod_capacity
    items_quantity = 0

    # Each item is a record from the 'CartProduct' model. It includes a product, a user, and a quantity.
    for item in cart.products.all():
        product = item.product
        if product.seller_user != product_db.seller_user:
            return JsonResponse(
                {"error" : "You cannot add products from different sellers to the same order."}, status=403
            )
        
        items_quantity += item.quantity
        if items_quantity >= max_prod_capacity:
            return JsonResponse(
                {"error" : "You cannot add more products in this order."}, status=403
            )
        
    cart_product = CartProduct(
        product = product_db,
        cart = cart,
        quantity = 1
    )

    cart_product.save()
    products_count = cart.products.count()

    return JsonResponse(
        {"products_count" : products_count}, status=200
    )

# Deletes cart item
@login_required
def delete_cart_item(request, product):

    product = Product.objects.filter(pk = product, deleted_at = None).first()

    if product:
        user = request.user
        cart = user.cart.all()
        productsCart = cart[0].products.all()

        for prodCart in productsCart:
            if prodCart.product == product:
                prodCart.delete()

                # Redirect if there are no items in the cart
                redirect = False
                if len(productsCart) - 1 == 0:
                    redirect = True
                
                return JsonResponse(
                    {"result" : True, "redirect" : redirect}, status = 200
                )
    else:
        return JsonResponse(
            {"result" : False}, status = 400
        )

# New Order
@login_required
def create_order(request):
    
    if request.method == "POST":

        data = json.loads(request.body)

        date = data["date"]
        products = data["products"]

        products_db = []
        seller_user = None
        order_total_amount = 0
        order_total_quantity = 0

        for product in products:
            prod_db = Product.objects.filter(pk = product["id"], deleted_at = None).first()
            
            if prod_db:
                try:
                    # Validation
                    int(product["quantity"])
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    date_obj = timezone.make_aware(date_obj, timezone.get_current_timezone())

                    if int(product["quantity"]) < 1 or int(product["quantity"]) > 10: # Max product quantity
                        return JsonResponse({'status': 'error', 'message': 'Quantity must be between 1 and 10'}, status=400)
                    if not prod_db.availability:
                        # Deletes this product of the cart
                        cart = request.user.cart.get()
                        products_cart = cart.products.all()

                        for product_cart in products_cart:
                            product_cart.delete()

                        return JsonResponse({'status': 'error', 'message': f"The '{prod_db.name}' is not available"}, status=400)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)
                except KeyError:
                    return JsonResponse({'status': 'error', 'message': 'Missing quantity in product data'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Something was wrong'}, status = 400)

            prod_db.quantity = int(product["quantity"])
            seller_user = prod_db.seller_user

            # Accumulates product quantity
            order_total_quantity = order_total_quantity + int(product["quantity"])

            # Calculates total amount again
            ingredients = prod_db.ingredients.filter(deleted_at = None)    
            prod_db.total_price = float(prod_db.subtotal_price)
            for productIngredient in ingredients:
                prod_db.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

            total_item = prod_db.total_price * prod_db.quantity
            order_total_amount += total_item

            products_db.append(prod_db)

        # NOTE: Validation of delivery date, quantities and total amount

        # Looks for the date within the days_off
        day_off = seller_user.days_off.filter( date = date_obj ).first()

        # Validates if it isn't a day off
        if day_off:
            return JsonResponse({'status': 'error', 'message': 'Invalid date'}, status = 400)

        prev_orders = Order.objects.filter(seller_user = seller_user, deleted_at = None, delivery_date = date_obj, archived = False)
        max_prod_per_day = seller_user.max_prod_capacity

        # Calculates total quantities
        count_previous_products = 0
        for order in prev_orders:
            count_quantity = order.products.aggregate(total=Sum('quantity'))
            count_previous_products += count_quantity['total'] or 0 # Assign 0 instead of None

        # Validates the quantitites for this day
        if count_previous_products + order_total_quantity > max_prod_per_day:

            # NOTE: Patch for Safari, it has problems with the day picker library

            invalid_dates_response = check_dates(request, order_total_quantity, seller_user.id)
            invalid_dates = json.loads(invalid_dates_response.content.decode('utf-8'))

            return JsonResponse({
                'status': 'error',
                'message': 'Invalid quantity',
                'prev_invalid_dates': invalid_dates['disabled_days']

            }, status = 400)
        
        # Generates unique token
        token = generate_unique_token()

        # Creates order
        order = Order(
            buyer_user = request.user,
            seller_user = seller_user,
            total_amount = order_total_amount,
            delivery_date = date_obj,
            token = token
        )
        order.save()

        # Creates each order's item
        for prod in products_db:
            OrderProduct.objects.create(
                product = prod,
                quantity = prod.quantity,
                order = order
            )
        
        # Delete Cart
        user_cart = request.user.cart.get()
        user_cart.delete() 

        # Create Notifications
        notification_seller = Notification(
            user = seller_user,
            notification_type = 'order',
            message = f"You have a new order (#{token}) awaiting your approval. Please review it under 'Pending Orders' and update the order status as soon as possible."
        )
        
        notification_seller.save()

        notification_buyer = Notification(
            user = request.user,
            notification_type = 'order',
            message = f"Your order (#{token}) has been submitted to the seller. Please wait for their approval. We will notify you once the order status is updated."
        )

        notification_buyer.save()

        return JsonResponse({'status': 'success', 'order_id': order.id}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 403)
    
# Deletes order
@login_required
def delete_order(request, order):

    order_db = Order.objects.filter(pk = order, deleted_at = None).first()

    if( order_db and order_db.seller_user == request.user):

        order_db.deleted_at = timezone.now()
        order_db.save()

        # Create Notifications
        notification_seller = Notification(
            user = order_db.seller_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been deleted."
        )
        
        notification_seller.save()

        notification_buyer = Notification(
            user = order_db.buyer_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been canceled by the seller."
        )

        notification_buyer.save()

        return JsonResponse({'status': 'success'}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 400)

# Confirms order
def confirm_order(request, order):

    order_db = Order.objects.filter(pk = order, deleted_at = None).first()

    if( order_db and order_db.seller_user == request.user):
        order_db.status = True
        order_db.save()

        # Create Notifications
        notification_seller = Notification(
            user = order_db.seller_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been confirmed."
        )
        
        notification_seller.save()

        notification_buyer = Notification(
            user = order_db.buyer_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been confirmed."
        )

        notification_buyer.save()
        
        return JsonResponse({'status': 'success'}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 400)
    
# Mark order as recived
def mark_recived(request, order):

    order_db = Order.objects.filter(pk = order, deleted_at = None).first()

    if( order_db and order_db.buyer_user == request.user):
        order_db.recived = True
        order_db.save()

        # Create Notifications
        notification_seller = Notification(
            user = order_db.seller_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been mark as recived by the buyer."
        )
        
        notification_seller.save()

        notification_buyer = Notification(
            user = order_db.buyer_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been mark as recived."
        )

        notification_buyer.save()

        return JsonResponse({'status': 'success'}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 400)
    

# Archive order
def archive_order(request, order):

    order_db = Order.objects.filter(pk = order, deleted_at = None, recived = True).first()

    if( order_db and order_db.seller_user == request.user):
        order_db.archived = True
        order_db.save()

        # Create Notifications
        notification_seller = Notification(
            user = order_db.seller_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been archived."
        )
        
        notification_seller.save()

        notification_buyer = Notification(
            user = order_db.buyer_user,
            notification_type = 'order',
            message = f"The order #{order_db.token} has been archived."
        )

        notification_buyer.save()

        return JsonResponse({'status': 'success'}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 400)