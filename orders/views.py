import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from .models import Cart, CartProduct, Order, OrderProduct
from products.models import Product



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

    if product_db in cart.products.all():
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

        for product in products:
            prod_db = Product.objects.filter(pk = product["id"], deleted_at = None).first()
            
            if prod_db:
                try:
                    # Validation
                    int(product["quantity"])
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    date_obj = timezone.make_aware(date_obj, timezone.get_current_timezone())

                    if int(product["quantity"]) < 1 or int(product["quantity"]) > 10:
                        return JsonResponse({'status': 'error', 'message': 'Quantity must be between 1 and 10'}, status=400)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)
                except KeyError:
                    return JsonResponse({'status': 'error', 'message': 'Missing quantity in product data'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Something was wrong'}, status = 400)

            prod_db.quantity = int(product["quantity"])
            seller_user = prod_db.seller_user

            # TODO Validar production time

            print('||| --- Chosed Date --- |||')
            print( date_obj )

            # Validates Date
            day_off = prod_db.seller_user.days_off.filter( date = date_obj ).first()
            print('||| --- Day Off --- ||| Deberia ser None')
            print(day_off)

            # Validates if it's a valid date

            # Validates if it isn't a day off
            if day_off:
                print(' BOOM !!')
                return JsonResponse({'status': 'error', 'message': 'Something was wrong'}, status = 400)


            prev_orders = Order.objects.filter(seller_user = seller_user, deleted_at = None, delivery_date = date_obj)
            count = 0




            # Calculates products per day (every product inside every order)
            for order in prev_orders:
                product_orders = order.products.filter(deleted_at = None)
                order.total_quantity = 0

                for prod_order in product_orders:
                    order.total_quantity += prod_order.quantity

                count += order.total_quantity





            print('||| --- Products Off Count --- |||')
            print(count)

            max_prod_per_day = seller_user.max_prod_capacity
            print('||| --- Max Day Prod --- |||')
            print(max_prod_per_day)





            # Calculates total amount again
            ingredients = prod_db.ingredients.filter(deleted_at = None)    
            prod_db.total_price = float(prod_db.subtotal_price)
            for productIngredient in ingredients:
                prod_db.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

            total_item = prod_db.total_price * prod_db.quantity
            order_total_amount += total_item

            products_db.append(prod_db)


    



        order = Order(
            buyer_user = request.user,
            seller_user = seller_user,
            total_amount = order_total_amount,
            delivery_date = date_obj
        )

        order.save()

        for prod in products_db:
            OrderProduct.objects.create(
                product = prod,
                quantity = prod.quantity,
                order = order
            )
        
        # Delete Cart
        user_cart = request.user.cart.get()
        user_cart.delete() 

        return JsonResponse({'status': 'success', 'order_id': order.id}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 403)
    

@login_required
def delete_order(request, order):

    order_db = Order.objects.filter(pk = order, deleted_at = None).first()

    if( order_db and order_db.seller_user == request.user):
        order_db.deleted_at = timezone.now()
        order_db.save()
        return JsonResponse({'status': 'success'}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 400)


def confirm_order(request, order):

    order_db = Order.objects.filter(pk = order, deleted_at = None).first()

    if( order_db and order_db.seller_user == request.user):
        order_db.status = True
        order_db.save()
        return JsonResponse({'status': 'success'}, status = 200)
    else:
        return JsonResponse({'status': 'error'}, status = 400)
    


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

        if prod.production_time > min_day:
            min_day = prod.production_time

        for productIngredient in ingredients:
            prod.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

        products.append(prod)

    if not seller_user or total_cart_quantity == 0 :
        return HttpResponseRedirect(reverse('index')) ## <<<<< <<

    # Calculates min date (with production time)
    today = datetime.now()
    time_zone_correction = min_day + 1 # NOTE: The production time calculation does not include the current day.
    min_date_formatted = (today + timedelta(days=time_zone_correction))

    # Look for seller days off
    disabled_days = seller_user.days_off.values_list('date', flat = True)

    # Look for all orders
    prev_orders = Order.objects.filter(seller_user = seller_user, deleted_at = None)

    max_prod_per_day = seller_user.max_prod_capacity

    for order in prev_orders:
        product_orders = order.products.filter(deleted_at = None)
        order.total_quantity = 0

        for prod_order in product_orders:
            order.total_quantity += prod_order.quantity

        if ( order.total_quantity + total_cart_quantity ) > max_prod_per_day:
            disabled_days.append(order.delivery_date)

    # Removes any duplicates
    disabled_days = list(set(disabled_days))

    # ISO Format
    disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]  # Formato ISO

    return render(request, 'orders/checkout.html', {
        "products" : products,
        "seller_user" : seller_user,
        "disabled_days" : json.dumps(disabled_days_list),
        "min_day": min_date_formatted.strftime("%Y-%m-%d"),
        "min_day_number": min_day
    })

# Pending Orders view (seller)
@login_required
def pending_orders(request):
    
    orders = Order.objects.filter(seller_user = request.user, deleted_at = None).all()

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


# Pending Orders view (buyer)
@login_required
def pending_deliveries(request):

    orders = Order.objects.filter(buyer_user = request.user, deleted_at = None).all()

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

    return render(request, 'orders/pending_deliveries.html', {
        "page": page
    })