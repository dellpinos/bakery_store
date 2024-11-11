import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime
from orders.models import Order
from users.models import SellerTimeOff, User
from products.models import Product, Ingredient


# Dashboard Information view
@login_required
def index(request):
    return render(request, "dashboard/index.html")

# All products view
@login_required
def all_products(request):

    products = Product.objects.filter(seller_user = request.user, deleted_at = None).order_by("-created_at")

    # Calculates total price
    for product in products:
        ingredients = product.ingredients.filter(deleted_at = None)

        if not ingredients:
            return render(request, "dashboard/index.html", {
                "message": f"The product | ID: {product.id}, Name:{product.name} | has no valid ingredients"
            })

        product.total_price = float(product.subtotal_price)

        for productIngredient in ingredients:
            product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

    # Paginator
    p = Paginator(products, 20) # NOTE: Items per page

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, "dashboard/products.html", {
        "page": page
    })

# All ingredients view
@login_required
def all_ingredients(request):

    ingredients = Ingredient.objects.filter(seller_user = request.user, deleted_at = None).order_by("-created_at")

    # Paginator
    p = Paginator(ingredients, 20) # NOTE: Items per page

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, "dashboard/ingredients.html", {
        "page": page
    })

# Settings view
@login_required
def settings(request):

    orders = Order.objects.filter(seller_user = request.user, deleted_at = None, archived = False)
    pending_dates = []

    # Look for pending orders
    for order in orders:
        pending_dates.append(order.delivery_date)

    # Look for previous days off
    days_off = request.user.days_off.values_list('date', flat=True)

    # ISO Format
    pending_dates_list = [day.strftime('%Y-%m-%d') for day in pending_dates]
    days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]

    capacity = request.user.max_prod_capacity
    
    return render(request, "dashboard/settings.html", {
        "days_off": json.dumps(days_off_list),
        "pending_dates": json.dumps(pending_dates_list),
        "capacity": capacity
    })

# Update calendar in the settings view
@login_required
def calendar_update(request):
 
    if (request.POST):
        body = request.POST
        str_dates = body["dates"]
        obj_dates = []

        if str_dates:
            dates = str_dates.split(", ")

            # Date format validation
            try:
                for date in dates:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    date_obj = timezone.make_aware(date_obj, timezone.get_current_timezone())
                    obj_dates.append(date_obj)
            except:
                return render(request, "dashboard/settings.html", {
                    "message": {
                        "type": "error",
                        "txt": "Invalid date"
                    }
                })

            # Deletes previous days off
            prev_dates = request.user.days_off.all()

            for prev_date in prev_dates:
                prev_date.delete()

            for date in obj_dates:
                new_date = SellerTimeOff(
                    user = request.user,
                    date = date
                )

                new_date.save()
        else:
            # Deletes previous days off
            prev_dates = request.user.days_off.all()

            for prev_date in prev_dates:
                prev_date.delete()

        capacity = request.user.max_prod_capacity
        days_off = request.user.days_off.values_list('date', flat=True)
        days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]  # ISO Format

        return render(request, "dashboard/settings.html", {
            "message": {
                "type": "success",
                "txt": "Days off updated"
            },
            "days_off": json.dumps(days_off_list),
            "capacity": capacity
        })

# Update the user's maximum daily production in the settings view
@login_required
def capacity_update(request):
        
    if request.POST:
        body = request.POST
        new_capacity = body["capacity"]

        capacity = request.user.max_prod_capacity
        days_off = request.user.days_off.values_list('date', flat=True)
        days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]  # ISO Format

        try:
            int(new_capacity)
            if int(new_capacity) < 1 or int(new_capacity) > 10:
                raise Exception
        except:
            return render(request, "dashboard/settings.html", {
                "message": {
                    "type": "error",
                    "txt": "Invalid production capacity"
                },
                "days_off": json.dumps(days_off_list),
                "capacity": capacity
            })

        user = request.user
        user.max_prod_capacity = new_capacity

        user.save()

        return render(request, "dashboard/settings.html", {
            "message": {
                "type": "success",
                "txt": "Capacity updated"
            },
            "days_off": json.dumps(days_off_list),
            "capacity": new_capacity
        })
    
@login_required
def disable_all(request):

    if request.POST:

        orders = Order.objects.filter(seller_user = request.user, deleted_at = None, archived = False)
        pending_dates = []

        # Look for pending orders
        for order in orders:
            pending_dates.append(order.delivery_date)

        # Look for previous days off
        days_off = request.user.days_off.values_list('date', flat = True)

        # ISO Format
        pending_dates_list = [day.strftime('%Y-%m-%d') for day in pending_dates]
        days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]

        capacity = request.user.max_prod_capacity
        
        if orders.exists():
            return render(request, "dashboard/settings.html", {
                "message": {
                    "type": "error",
                    "txt": "There are pending orders"
                },
                "days_off": json.dumps(days_off_list),
                "pending_dates": json.dumps(pending_dates_list),
                "capacity": capacity
            })

        # Disable all products
        products = Product.objects.filter(seller_user = request.user, deleted_at = None)

        for product in products:
            product.availability = False
            product.save()

        return render(request, "dashboard/settings.html", {
            "message": {
                "type": "success",
                "txt": "All products have been disabled"
            },
            "days_off": json.dumps(days_off_list),
            "pending_dates": json.dumps(pending_dates_list),
            "capacity": capacity
        })


## API ##

# Get seller's disabled days
@login_required
def check_dates(request, quantity, user): 

    seller_user = User.objects.filter(pk = user).first()
    max_prod_per_day = seller_user.max_prod_capacity

    # Look for seller days off
    disabled_days = list(seller_user.days_off.values_list('date', flat = True))

    # Look for all orders
    prev_orders = Order.objects.filter(seller_user = seller_user, deleted_at = None, archived = False)

    # Iterates all orders to get a list of elements (date, order.id and total_quantity)
    order_products_summary = []

    for order in prev_orders:
        # Sum all the products from each order
        total_quantity = order.products.aggregate(total=Sum('quantity'))
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
        if ( summary['total_products'] + quantity ) > max_prod_per_day:
            disabled_days.append(summary['date'])

    # Removes any duplicates
    disabled_days = list(set(disabled_days))

    # ISO Format
    disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]

    return JsonResponse({'status': 'success', "disabled_days": json.dumps(disabled_days_list)})