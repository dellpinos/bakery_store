from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from products.models import Product, Category, Ingredient
from users.models import SellerTimeOff

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
def settings(request):

    # Cambiar 2 por el número escogido por este usuario en el otro formulario

    # min_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    # days_off = request.user.days_off.all()

    # days_off_list = list(days_off.values())

    capacity = request.user.max_prod_capacity
    days_off = request.user.days_off.values_list('date', flat=True)
    days_off_list = [day.strftime('%Y-%m-%d') for day in days_off]  # Formato ISO
    
    return render(request, "dashboard/settings.html", {
        "days_off": json.dumps(days_off_list),
        "capacity": capacity
    })

    # return render(request, "dashboard/calendar.html", {
    #     "min_date" : min_date
    # })

@login_required
def calendar_update(request):

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



