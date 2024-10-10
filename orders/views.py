from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse

from .models import Cart, CartProduct
from products.models import Product, Ingredient


## API ##

@csrf_exempt
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
            ingredients = product.ingredients.all()
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


# Add new product 
@csrf_exempt
@login_required
def create_cart(request, product):

    product_db = Product.objects.filter(pk=product).first()

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

@csrf_exempt
@login_required
def checkout(request):
    
    cart = request.user.cart.get()
    cart_products = cart.products.all()
    products = []

    for cart_prod in cart_products:

        prod = cart_prod.product
        ingredients = prod.ingredients.all()
        prod.total_price = float(prod.subtotal_price)

        for productIngredient in ingredients:
            prod.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

        products.append(prod)

    return render(request, 'orders/checkout.html', {
        "products" : products
    })