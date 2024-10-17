from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta
from django.urls import reverse
from django.core.paginator import Paginator
from products.models import Product, Category, Ingredient
from users.models import SellerTimeOff, User
from orders.models import Order, OrderProduct
from django.http import HttpResponseRedirect, JsonResponse

import json




@login_required
def index(request):

    return render(request, "dashboard/index.html")

@login_required
def all_products(request):

    products = Product.objects.filter(seller_user=request.user).order_by("-created_at")

    # Calculates total price
    for product in products:
        ingredients = product.ingredients.all()
        product.total_price = float(product.subtotal_price)

        for productIngredient in ingredients:
            product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size


    # Paginator
    p = Paginator(products, 20)

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, "dashboard/products.html", {
        "page": page
    })

@login_required
def all_ingredients(request):

    ingredients = Ingredient.objects.filter(seller_user=request.user).order_by("-created_at")

    # Paginator
    p = Paginator(ingredients, 20)

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, "dashboard/ingredients.html", {
        "page": page
    })

@login_required
def pending_orders(request):
    
    orders = Order.objects.filter(seller_user = request.user).all()

    

    for order in orders:
        order_products = order.products.all()
        order.products_list = []
        order.total_products = 0

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
    p = Paginator(orders, 20)

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, 'dashboard/pendings.html', {
        "page": page
    })


@login_required
def settings(request):

    # Cambiar 2 por el número escogido por este usuario en el otro formulario

    # min_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    # days_off = request.user.days_off.all()

    # days_off_list = list(days_off.values())

    orders = Order.objects.filter(seller_user = request.user).all()
    pending_dates = []

    for order in orders:
        pending_dates.append(order.delivery_date)


    capacity = request.user.max_prod_capacity
    days_off = request.user.days_off.values_list('date', flat=True)
    
    pending_dates_list = [day.strftime('%Y-%m-%d') for day in pending_dates]  # Formato ISO
    days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]  # Formato ISO
    
    return render(request, "dashboard/settings.html", {
        "days_off": json.dumps(days_off_list),
        "pending_dates": json.dumps(pending_dates_list),
        "capacity": capacity
    })

    # return render(request, "dashboard/calendar.html", {
    #     "min_date" : min_date
    # })

@login_required
def calendar_update(request):

 ## Escribir valdiacion para verificar que los request si o si son post, un IF al principio de cada método POST
 
    body = request.POST
    str_dates = body["dates"]

    if str_dates:

        dates = str_dates.split(", ")

        # Date format validation
        try:
            for date in dates:
                datetime.strptime(date, "%Y-%m-%d")

        except:
            return render(request, "dashboard/settings.html", {
                "message": {
                    "type": "error",
                    "txt": "Invalid date"
                }
            })

        prev_dates = request.user.days_off.all()

        for prev_date in prev_dates:
            prev_date.delete()

        for date in dates:

            new_date = SellerTimeOff(
                user = request.user,
                date = date
            )

            new_date.save()
    else:
        prev_dates = request.user.days_off.all()

        for prev_date in prev_dates:
            prev_date.delete()

    capacity = request.user.max_prod_capacity
    days_off = request.user.days_off.values_list('date', flat=True)
    days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]  # Formato ISO

    return render(request, "dashboard/settings.html", {
        "message": {
            "type": "success",
            "txt": "Days off updated"
        },
        "days_off": json.dumps(days_off_list),
        "capacity": capacity
    })

@login_required
def capacity_update(request):
        
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
def check_dates(request, quantity, user): 

    seller_user = User.objects.filter(pk = user).first() # Vendedor
    max_prod_per_day = seller_user.max_prod_capacity # Máximo por dia

    disabled_days = list(seller_user.days_off.values_list('date', flat = True))


    # Buscar todas las ordenes
    prev_orders = Order.objects.filter(seller_user = seller_user).all() # Todas las ordenes

    for order in prev_orders:
        product_orders = order.products.all()
        order.total_quantity = 0

        for prod_order in product_orders:
            order.total_quantity += prod_order.quantity

        if ( order.total_quantity + quantity ) > max_prod_per_day:
            disabled_days.append(order.delivery_date)


    # Crear un array de fechas cuya cantidad de productos sumada al quantity recibido supere el max_prod_per_day
    # Agregar disabled_days a este array


    disabled_days = list(set(disabled_days))

    disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]  # Formato ISO

    return JsonResponse({'status': 'success', "disabled_days": json.dumps(disabled_days_list)})
