from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse

from .models import Cart
from products.models import Product, Ingredient

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


    # Enviar elementos para listar

    products_count = cart.products.count()

    if products_count > 0:
        products = cart.products.all()
        serialized_products = []

        # Calculates total price
        for product in products:
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




@csrf_exempt
@login_required
def create_cart(request, product):

    product_db = Product.objects.filter(pk=product).first()

    if product_db is None:
        return JsonResponse(
            {"error" : "Forbidden"}, status = 403
        )
    
    cart = Cart.objects.filter(user=request.user).first()

    if cart is None:
        cart = Cart(
            user = request.user
        )
        cart.save()
        
    if product_db in cart.products.all():
        return JsonResponse(
            {"error" : "Product already in cart"}, status=403
        )



    cart.products.add(product_db)

    products_count = cart.products.count()



# Retorno la cantidad de productos actuales para la notificación del icono

    return JsonResponse(
        {"products_count" : products_count}, status=200
    )
    pass