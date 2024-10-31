from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
import json, random
from .models import Product, Category, Ingredient, ProductIngredient
from orders.models import Cart, OrderProduct


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

## Public Controllers ##

# Index view
def home(request):

    # User Cart
    cart_seller = None
    if request.user.is_authenticated:
        try:
            cart = request.user.cart.get()
            products_cart = cart.products.all()

            for cart_prod in products_cart:
                cart_seller = cart_prod.product.seller_user

        except Cart.DoesNotExist:
            pass

    if cart_seller:
        products = Product.objects.filter(availability = True, seller_user = cart_seller, deleted_at = None).order_by('-created_at')
    else:
        products = Product.objects.filter(availability=True, deleted_at = None).order_by('-created_at')

    # Calculates total price
    for product in products:
        ingredients = product.ingredients.filter(deleted_at = None)
        product.total_price = float(product.subtotal_price)

        for productIngredient in ingredients:
            product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

    categories = Category.objects.all()

    return render(request, "home/index.html", {
        "products": products,
        "cart_seller": cart_seller,
        "categories": categories
    })

# Index filtered by category
def home_filtered(request, category):

    category_db = Category.objects.filter(pk = category).first()

    if not category:
        return HttpResponseRedirect(reverse("index", {
                "message": "Invalid category"
        }))
    
    
    # User Cart
    cart_seller = None
    if request.user.is_authenticated:
        try:
            cart = request.user.cart.get()
            products_cart = cart.products.all()

            for cart_prod in products_cart:
                cart_seller = cart_prod.product.seller_user

        except Cart.DoesNotExist:
            pass

    if cart_seller:
        products = Product.objects.filter(availability = True, seller_user = cart_seller, deleted_at = None, categories__id = category_db.id).order_by('-created_at')
    else:
        products = Product.objects.filter(availability=True, deleted_at = None, categories__id = category_db.id).order_by('-created_at')

    # Calculates total price
    for product in products:
        ingredients = product.ingredients.filter(deleted_at = None)
        product.total_price = float(product.subtotal_price)

        for productIngredient in ingredients:
            product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

    categories = Category.objects.all()

    return render(request, "home/index.html", {
        "products": products,
        "cart_seller": cart_seller,
        "categories": categories,
        "category_db": category_db

    })

# Returns the show view of a random product
def random_product(request):

    product_ids = list(Product.objects.filter(availability = True).values_list('id', flat=True))

    # Verify if there are any products
    if product_ids:
        # Random ID select
        random_id = random.choice(product_ids)
        print(f'Random Product ID: {random_id}')
    else:
        print('No products found.')

    product = Product.objects.filter(pk = random_id, deleted_at = None).first()

    ingredients = product.ingredients.filter(deleted_at = None)
    product.total_price = float(product.subtotal_price)

    for productIngredient in ingredients:
        product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

    # Looks for related products by the same seller (limit: 3)
    products = list(Product.objects.filter(seller_user = product.seller_user).exclude(pk=product.id).order_by('-created_at')[:3])

    # Initialize with excluded IDs
    excluded_ids = [product.id for product in products]
    excluded_ids.append(product.id)

    missing_products = 3 - len(products)

    while missing_products > 0:
            
        # Find a product that does not appear in the excluded list.
        new_product = Product.objects.exclude(pk__in=excluded_ids).filter(deleted_at=None).order_by('-created_at').first()

        # Break if there are no more products
        if not new_product:
            break

        products.append(new_product)
        excluded_ids.append(new_product.id)

        missing_products -= 1

    categories = Category.objects.all()

    return render(request, "home/show_product.html", {
        "product": product,
        "related_products": products,
        "categories": categories
    })

# View that displays all the information of a product (show view)
def show_product(request, product):

    product = Product.objects.filter(pk=product, deleted_at=None).first()

    if product is None or not product.availability:
        return HttpResponseRedirect(reverse("index"))

    ingredients = product.ingredients.filter(deleted_at = None)
    product.total_price = float(product.subtotal_price)

    for productIngredient in ingredients:
        product.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

    # Looks for related products by the same seller (limit: 3)
    products = list(Product.objects.filter(seller_user = product.seller_user, availability = True).exclude(pk=product.id).order_by('-created_at')[:3])

    # Initialize with excluded IDs
    excluded_ids = [product.id for product in products]
    excluded_ids.append(product.id)

    missing_products = 3 - len(products)

    while missing_products > 0:
            
        # Find a product that does not appear in the excluded list.
        new_product = Product.objects.exclude(pk__in=excluded_ids).filter(availability = True, deleted_at = None).order_by('-created_at').first()

        # Break if there are no more products
        if not new_product:
            break

        products.append(new_product)
        excluded_ids.append(new_product.id)

        missing_products -= 1

    # User Cart
    in_cart = False
    cart_seller_id = None

    # Check if the product is in the cart
    if request.user.is_authenticated:
        try:
            if request.user.cart.get():
                cart = request.user.cart.get()
                products_cart = cart.products.all() # All the CartProduct
                
                for cart_prod in products_cart:
                    cart_seller_id = cart_prod.product.seller_user.id # Every product

                    if cart_prod.product == product:
                        in_cart = True

        except Cart.DoesNotExist:
            pass

    categories = Category.objects.all()

    return render(request, "home/show_product.html", {
        "product": product,
        "related_products": products,
        "in_cart": in_cart,
        "cart_seller_id": cart_seller_id,
        "categories" : categories
    })



## Dashboard Controllers ##

# New product form
@login_required
def new_product(request):

    if request.method == 'POST':

        body = request.POST
        ingredients = [json.loads(item) for item in body.getlist('ingredient_data')]
        categories_list = body.getlist('categories')

        # Validation
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

        # Gets user's ingredients
        for ingredient in ingredients:

            ingredient_db = Ingredient.objects.filter(pk = ingredient['id'], deleted_at = None).first()
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
            categories = Category.objects.filter(deleted_at = None)
            ingredients_all = Ingredient.objects.filter(seller_user = request.user, availability = True, deleted_at = None).order_by("name")
            return render(request, "dashboard/create_product.html", {
                "errors": errors,
                "body": body,
                "ingredient_list": ingredients_db,
                "categories_list": categories_list_int,
                "ingredients": ingredients_all,
                "categories": categories
            })
        
        else:
            # Save new product
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
        ingredients = Ingredient.objects.filter(seller_user = request.user, availability = True, deleted_at = None).order_by("name")
        
        return render(request, "dashboard/create_product.html", {
            "categories": categories,
            "ingredients": ingredients
        })
    

# Edit product form
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

        # Gets user's ingredients
        for ingredient in ingredients:
            ingredient_db = Ingredient.objects.filter(pk = ingredient['id'], seller_user = request.user, deleted_at = None).first()
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

            categories = Category.objects.filter(deleted_at = None)
            ingredients_all = Ingredient.objects.filter(seller_user = request.user, availability = True, deleted_at = None).order_by("name")
            return render(request, "dashboard/create_product.html", {
                "errors": errors,
                "product": body,
                "ingredient_list": ingredients_db,
                "categories_list": categories_list_int,
                "ingredients": ingredients_all,
                "categories": categories
            })
        else:

            product_db = Product.objects.filter(pk=product, seller_user = request.user, deleted_at = None).first()
            if product_db is None:
                return HttpResponseRedirect(reverse("dashboard_products"))

            # Save new data
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

        product = Product.objects.filter(pk=product, seller_user = request.user, deleted_at = None).first()
        if product is None:
            return HttpResponseRedirect(reverse("dashboard_products"))

        ingredients_prev = []

        for ingredient in product.ingredients.filter( deleted_at = None ):

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
        ingredients_all = Ingredient.objects.filter(seller_user=request.user, availability = True, deleted_at = None).order_by("name")
        
        return render(request, "dashboard/edit_product.html", {
            "categories": categories,
            "product": product,
            "ingredient_list": ingredients_prev,
            "categories_list": categories_list_int,
            "ingredients": ingredients_all,
            "categories_prev": product.categories
        })
    
# New ingredient form
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
                "message": "Invalid value"
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

# Edit ingredient form
@login_required
def edit_ingredient(request, ingredient):

    ingredient_db = Ingredient.objects.filter(pk = ingredient, seller_user = request.user, deleted_at = None).first()
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
                "message": "Invalid value"
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


## API ##

# Changes product's availability
@login_required
def product_availability(request, product):

    product_db = Product.objects.filter(pk = product, seller_user = request.user, deleted_at = None).first()
    if product_db is None:
        return JsonResponse(
            {"error" : "Forbidden"}, status=403
        )
    
    # Look for pendient orders with this product
    order_products = OrderProduct.objects.filter(product = product_db, deleted_at = None)


    for order_prod in order_products:
        order = order_prod.order
        # Only active orders
        if order.deleted_at == None:
            return JsonResponse(
                {"error" : "There are open orders with this product; you should confirm or close them first."}, status=403
            )

    if product_db.availability:
        product_db.availability = False
    else:
        product_db.availability = True
    product_db.save()

    return JsonResponse(
        {"item" : {
            "name" : product_db.name,
            "availability" : product_db.availability
        }}, status=200
    )