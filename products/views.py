from django.shortcuts import render
from .models import Product, Category, Ingredient, ProductIngredient

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import json



## Validation ##
def ingredient_validation(body, new):

    errors = []
    if len(body["name"]) < 3 or len(body["name"]) > 120 :
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
    

def product_validation(body, ingredients):

    errors = []

    if len(body["name"]) < 3 or len(body["name"]) > 120 :
        errors.append('The name must be between 5 and 120 characters long.')

    if len(body["image"]) > 240:
        errors.append('Invalid URL format in image field.')

    if len(body["description"]) > 550:
        errors.append('The description must be under 120 characters long.')

    if float(body["price"]) <= 0 or float(body["price"]) > 999999:
        errors.append('The price must be greater than 1 and less than 999,999.')

    if int(body["prod_time"]) <= 0 or int(body["prod_time"]) > 99:
        errors.append('The production time must be greater than 1 and less than 99.')

    for ingredient in ingredients:
        if float(ingredient["quantity"]) < 0 or float(ingredient["quantity"]) > 999999:
            errors.append('The ingredient quantity must be greater than 1 and less than 999,999.')

    return errors

## Controllers ##

def home(request):

    products = Product.objects.order_by('-created_at')

    # Calculates total price
    for product in products:
        ingredients = product.ingredients.all()
        product.total_price = float(product.subtotal_price)

        for productIngredient in ingredients:
            product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

    return render(request, "home/index.html", {
        "products": products
    })

@login_required
def show_product(request, product):

        product = Product.objects.filter(pk=product, seller_user=request.user).first()
        if product is None:
            return HttpResponseRedirect(reverse("dashboard_products"))

        ingredients_prev = []

        for ingredient in product.ingredients.all():

            ingredients_prev.append({
                "id" : ingredient.ingredient.id,
                "quantity" : ingredient.quantity,
                "name" : ingredient.ingredient.name,
                "size" : ingredient.ingredient.size,
                "measurement_unit" : ingredient.ingredient.measurement_unit,
                "price" : ingredient.ingredient.price 
            })

        categories_list_int = []

        for cat in product.categories.all():
            categories_list_int.append(int(cat.id))

        categories = Category.objects.all()
        ingredients_all = Ingredient.objects.filter(seller_user=request.user, availability=True).order_by("name")
        
        return render(request, "home/show_product.html", {
            "categories": categories,
            "product": product,
            "ingredient_list": ingredients_prev,
            "categories_list": categories_list_int,
            "ingredients": ingredients_all,
            "categories_prev": product.categories
        })

# Dashboard







@login_required
def new_product(request):

    if request.method == 'POST':

        body = request.POST
        ingredients = [json.loads(item) for item in body.getlist('ingredient_data')]
        categories_list = body.getlist('categories')

        try:
            int(body["prod_time"])
            float(body["price"])
            for category in categories_list:
                int(category)
            for ingredient in ingredients:
                int(ingredient['id'])
                float(ingredient['quantity'])

        except (ValueError):
            return render(request, "dashboard/create_product.html", {
                "message": "Invalid value"
            })
        
        errors = product_validation(body, ingredients)

        ingredients_db = []
        categories_db = []
        categories_list_int = []

        for ingredient in ingredients:

            ingredient_db = Ingredient.objects.filter(pk=ingredient['id']).first()
            if ingredient_db is None:
                return HttpResponseRedirect(reverse("dashboard_products"))
            
            ingredient_db.quantity = ingredient["quantity"]

            if not ingredient_db:
                errors.append('Invalid ingredient')

            if ingredient_db.seller_user != request.user:
                errors.append('Invalid ingredient')

            ingredients_db.append(ingredient_db)

        for category in categories_list:

            category_db = Category.objects.filter(pk=category).first()
            if category_db is None:
                errors.append('Invalid category')

            categories_db.append(category_db)
            categories_list_int = [int(category) for category in categories_list]

        if len(errors) != 0:

            categories = Category.objects.all()
            ingredients_all = Ingredient.objects.filter(seller_user=request.user, availability=True).order_by("name")
            return render(request, "dashboard/create_product.html", {
                "errors": errors,
                "body": body,
                "ingredient_list": ingredients_db,
                "categories_list": categories_list_int,
                "ingredients": ingredients_all,
                "categories": categories
            })
        else:

            new_product = Product(
                name = body["name"],
                subtotal_price = float(body["price"]),
                description = body["description"],
                image = body["image"],
                production_time = int(body["prod_time"]),
                seller_user = request.user,
            )

            new_product.save()

            for category in categories_db:
                new_product.categories.add(category)

            for ingredient in ingredients_db:

                productIngredient = ProductIngredient(
                    product = new_product,
                    ingredient = ingredient,
                    quantity = ingredient.quantity
                )

                productIngredient.save()
            return HttpResponseRedirect(reverse("dashboard_products"))

    else:
        categories = Category.objects.all()
        ingredients = Ingredient.objects.filter(seller_user=request.user, availability=True).order_by("name")
        
        return render(request, "dashboard/create_product.html", {
            "categories": categories,
            "ingredients": ingredients
        })
    
@login_required
def edit_product(request, product):

    if request.method == 'POST':

        body = request.POST
        ingredients = [json.loads(item) for item in body.getlist('ingredient_data')]
        categories_list = body.getlist('categories')

        try:
            int(body["prod_time"])
            float(body["price"])
            for category in categories_list:
                int(category)
            for ingredient in ingredients:
                int(ingredient['id'])
                float(ingredient['quantity'])

        except (ValueError):
            return render(request, "dashboard/create_product.html", {
                "message": "Invalid value"
            })
        
        errors = product_validation(body, ingredients)

        ingredients_db = []
        categories_db = []
        categories_list_int = []

        for ingredient in ingredients:
            ingredient_db = Ingredient.objects.filter(pk=ingredient['id'], seller_user=request.user).first()
            ingredient_db.quantity = ingredient["quantity"]

            if ingredient_db is None:
                errors.append('Invalid ingredient')

            if ingredient_db.seller_user != request.user:
                errors.append('Invalid ingredient')

            ingredients_db.append(ingredient_db)

        for category in categories_list:

            category_db = Category.objects.filter(pk=category).first()
            if category_db is None:
                errors.append('Invalid category')

            categories_db.append(category_db)
            categories_list_int = [int(category) for category in categories_list]

        if len(errors) != 0:

            categories = Category.objects.all()
            ingredients_all = Ingredient.objects.filter(seller_user=request.user, availability=True).order_by("name")
            return render(request, "dashboard/create_product.html", {
                "errors": errors,
                "product": body,
                "ingredient_list": ingredients_db,
                "categories_list": categories_list_int,
                "ingredients": ingredients_all,
                "categories": categories
            })
        else:

            product_db = Product.objects.filter(pk=product, seller_user=request.user).first()
            if product_db is None:
                return HttpResponseRedirect(reverse("dashboard_products"))

            product_db.name = body["name"]
            product_db.subtotal_price = float(body["price"])
            product_db.description = body["description"]
            product_db.image = body["image"]
            product_db.production_time = int(body["prod_time"])

            product_db.save()

            # Delete previous relationships
            product_db.categories.clear()
            ProductIngredient.objects.filter(product=product_db).delete()

            for category in categories_db:
                product_db.categories.add(category)

            for ingredient in ingredients_db:

                productIngredient = ProductIngredient(
                    product = product_db,
                    ingredient = ingredient,
                    quantity = ingredient.quantity
                )

                productIngredient.save()

            return HttpResponseRedirect(reverse("dashboard_products"))

    else:

        product = Product.objects.filter(pk=product, seller_user=request.user).first()
        if product is None:
            return HttpResponseRedirect(reverse("dashboard_products"))

        ingredients_prev = []

        for ingredient in product.ingredients.all():

            ingredients_prev.append({
                "id" : ingredient.ingredient.id,
                "quantity" : ingredient.quantity,
                "name" : ingredient.ingredient.name,
                "size" : ingredient.ingredient.size,
                "measurement_unit" : ingredient.ingredient.measurement_unit,
                "price" : ingredient.ingredient.price 
            })

        categories_list_int = []

        for cat in product.categories.all():
            categories_list_int.append(int(cat.id))

        categories = Category.objects.all()
        ingredients_all = Ingredient.objects.filter(seller_user=request.user, availability=True).order_by("name")
        
        return render(request, "dashboard/edit_product.html", {
            "categories": categories,
            "product": product,
            "ingredient_list": ingredients_prev,
            "categories_list": categories_list_int,
            "ingredients": ingredients_all,
            "categories_prev": product.categories
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

            return HttpResponseRedirect(reverse("dashboard_ingredients"))

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

    ingredient_db = Ingredient.objects.filter(pk=ingredient, seller_user=request.user).first()
    if ingredient_db is None:
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

# Hay que eliminar o limitar esta funcionalidad (que ocurre si el usuario elimina un ingrediente que es utilizado en productos)
@login_required
def delete_ingredient(request, ingredient):


    ingredient_db = Ingredient.objects.filter(pk=ingredient, seller_user=request.user).first()
    if ingredient_db is None:
        return HttpResponseRedirect(reverse("dashboard_ingredients"))
    
    ingredient_db.delete()
    
    return HttpResponseRedirect(reverse("dashboard_ingredients"))

## API ##

@csrf_exempt
@login_required
def ingredient_availability(request, ingredient):

    ingredient_db = Product.objects.filter(pk=ingredient, seller_user=request.user).first()
    if ingredient_db is None:
        return HttpResponseRedirect(reverse("dashboard_products"))

    # Auth
    if request.user != ingredient_db.seller_user:
        return JsonResponse(
            {"error" : "Forbidden"}, status=403
        )

    if ingredient_db.availability:
        ingredient_db.availability = False
    else:
        ingredient_db.availability = True
    ingredient_db.save()

    return JsonResponse(
        {"item" : ingredient_db.serialize()}, status=200
    )

@csrf_exempt
@login_required
def product_availability(request, product):

    product_db = Product.objects.filter(pk=product, seller_user=request.user).first()
    if product_db is None:
        return JsonResponse(
            {"error" : "Forbidden"}, status=403
        )

    if product_db.availability:
        product_db.availability = False
    else:
        product_db.availability = True
    product_db.save()

    return JsonResponse(
        {"item" : product_db.serialize()}, status=200
    )