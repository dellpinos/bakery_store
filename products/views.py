from django.shortcuts import render
from .models import Product, Category, Ingredient

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


## Validation ##
def ingredient_validation(body, new):

    errors = []
    if len(body["name"]) < 5 or len(body["name"]) > 120 :
        errors.append('The name must be between 5 and 120 characters long.')

    if len(body["description"]) > 550:
        errors.append('The description must be under 120 characters long.')

    if float(body["size"]) <= 0 or float(body["size"]) > 999999:
        errors.append('The size must be greater than 1 and less than 999,999.')
    
    if float(body["price"]) <= 0 or float(body["price"]) > 999999:
        errors.append('The price must be greater than 1 and less than 999,999.')
    
    if new:
        if len(body["measurement_unit"]) < 1 or len(body["measurement_unit"]) > 15:
            errors.append('The measurement unit must be between 1 and 15 characters long.')

    return errors


## Controllers ##
def home(request):

    products = Product.objects.order_by('-created_at')
    return render(request, "home/index.html", {
        "products": products
    })

# Dashboard
@login_required
def new_product(request):

    if request.method == 'POST':
        print('!!!')
        print(request.body)
        print('!!!')
    else:

        categories = Category.objects.all()
        ingredients = Ingredient.objects.filter(seller_user=request.user, availability=True).order_by("name")
        
        return render(request, "dashboard/create_product.html", {
            "categories": categories,
            "ingredients": ingredients
        })
    
@login_required
def new_ingredient(request):

    if request.method == 'POST':

        body = request.POST

        # Validation
        try:
            float(body["price"])
            float(body["size"])
        except (ValueError):
            return render(request, "dashboard/create_ingredient.html", {
                "message": "Invalid value."
            })

        errors = ingredient_validation(body, True)

        if len(errors) != 0:

            return render(request, "dashboard/create_ingredient.html", {
                "errors": errors,
                "body": body
            })
        else:
            ingredient = Ingredient(
                name = body["name"],
                description = body["description"],
                price = float(body["price"]),
                size = float(body["size"]),
                measurement_unit = body["measurement_unit"],
                seller_user = request.user
            )
            ingredient.save()

            return HttpResponseRedirect(reverse("dashboard")) # Cambiar a my ingredients

    return render(request, "dashboard/create_ingredient.html", {
        "body": {
            "name": "",
            "description": "",
            "size": "",
            "measurement_unit": "",
            "price": ""
        }
    })

@login_required
def edit_ingredient(request, ingredient):

    ingredient_db = get_object_or_404(Ingredient, pk=ingredient)

    # Auth
    if request.user != ingredient_db.seller_user:
        return HttpResponseRedirect(reverse("dashboard_ingredients"))

    if request.method == 'POST':

        body = request.POST

        # Validation
        try:
            float(body["price"])
            float(body["size"])
        except (ValueError):
            return render(request, "dashboard/edit_ingredient.html", {
                "message": "Invalid value."
            })

        errors = ingredient_validation(body, False)

        if len(errors) != 0:

            return render(request, "dashboard/edit_ingredient.html", {
                "errors": errors,
                "body": body
            })
        else:

            ingredient_db.name = body["name"]
            ingredient_db.description = body["description"]
            ingredient_db.price = float(body["price"])
            ingredient_db.size = float(body["size"])
            # ingredient_db.measurement_unit = body["measurement_unit"]

            ingredient_db.save()

            return HttpResponseRedirect(reverse("dashboard_ingredients"))

    return render(request, "dashboard/edit_ingredient.html", {
        "body": {
            "name": ingredient_db.name,
            "description": ingredient_db.description if ingredient_db.description else "",
            "size": ingredient_db.size,
            "measurement_unit": ingredient_db.measurement_unit,
            "price": ingredient_db.price
        },
        "ingredient": ingredient
    })
