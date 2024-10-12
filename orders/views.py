from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
import json

from .models import Cart, CartProduct, Order, OrderProduct
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



@login_required
def checkout(request):

    cart = request.user.cart.get()
    cart_products = cart.products.all()
    products = []
    seller_user = None

    for cart_prod in cart_products:

        prod = cart_prod.product
        ingredients = prod.ingredients.all()
        prod.total_price = float(prod.subtotal_price)
        prod.quantity = cart_prod.quantity
        seller_user = prod.seller_user

        for productIngredient in ingredients:
            prod.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

        products.append(prod)


    # A estos dias debo sumar aquellos que ya cumplen el cupo de capacidad máxima del vendedor
    # También incluir el dato de cuantas ordenes pendientes tiene el vendedor para esa fecha
    # Debe la disponibilidad de fechas debe ser dinámica si el usuario decide cambiar la cantidad de los productos

    prev_orders = Order.objects.filter(seller_user = seller_user).all()

    print(prev_orders)

    disabled_days = seller_user.days_off.values_list('date', flat = True)
    disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]  # Formato ISO


    return render(request, 'orders/checkout.html', {
        "products" : products,
        "seller_user" : seller_user,
        "disabled_days" : json.dumps(disabled_days_list),
    })


## API
@login_required
def create_order(request):
    

    date = request.POST['date']
    products = request.POST['products']



    products_dict = json.loads(products)

    print(products_dict)
    print(date)



# 'date': ['2024-10-24'],
# 'product_id_0': ['7'], 'product_quantity_0': ['1'],
# 'product_id_1': ['4'], 'product_quantity_1': ['1'],
# 'product_id_2': ['2'], 'product_quantity_2': ['1']
# Validar datos

# @csrf_exempt





        # products = None


        #     buyer_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "buyer_orders")
        #     seller_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "seller_orders")
        #     total_amount = models.DecimalField(max_digits = 10, decimal_places = 2)
        #     delivery_date = models.DateTimeField()

        # order = Order(
        #     buyer_user = request.user,
        #     seller_user = "",
        #     delivery_date = request.POST['date']

        # )
        # print(request.POST)
        # 1 dia
        # id de productos con cantidades
        # Comprador
        # Valor a abonar - Calcular
