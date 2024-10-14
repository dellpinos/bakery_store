from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse
import json
from datetime import datetime, timedelta

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
    total_cart_quantity = 0
    min_day = 0 # the longest production time in the current order

    for cart_prod in cart_products:

        prod = cart_prod.product
        ingredients = prod.ingredients.all()
        prod.total_price = float(prod.subtotal_price)
        prod.quantity = cart_prod.quantity
        seller_user = prod.seller_user
        total_cart_quantity += cart_prod.quantity
        if prod.production_time > min_day:
            min_day = prod.production_time

        for productIngredient in ingredients:
            prod.total_price += (productIngredient.quantity * float(productIngredient.ingredient.price)) / productIngredient.ingredient.size

        products.append(prod)


    # A estos dias debo sumar aquellos que ya cumplen el cupo de capacidad máxima del vendedor
    # También incluir el dato de cuantas ordenes pendientes tiene el vendedor para esa fecha
    # Debe la disponibilidad de fechas debe ser dinámica si el usuario decide cambiar la cantidad de los productos

    # Calculates min date (with production time)
    today = datetime.now()
    time_zone_correction = min_day - 1 ## Correción por zona horaria
    min_date_formatted = (today + timedelta(days=time_zone_correction))



    prev_orders = Order.objects.filter(seller_user = seller_user).all()


    disabled_days = seller_user.days_off.values_list('date', flat = True)

    disabled_days = list(set(disabled_days))
    # disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]  # Formato ISO





    ####

    max_prod_per_day = seller_user.max_prod_capacity # Máximo por dia


    # Buscar todas las ordenes

    for order in prev_orders:
        product_orders = order.products.all()
        order.total_quantity = 0

        for prod_order in product_orders:
            order.total_quantity += prod_order.quantity

        if ( order.total_quantity + total_cart_quantity ) > max_prod_per_day:
            disabled_days.append(order.delivery_date)


    # Crear un array de fechas cuya cantidad de productos sumada al quantity recibido supere el max_prod_per_day
    # Agregar disabled_days a este array




    disabled_days_list = [day.strftime('%Y-%m-%d') for day in disabled_days]  # Formato ISO




    ####



    return render(request, 'orders/checkout.html', {
        "products" : products,
        "seller_user" : seller_user,
        "disabled_days" : json.dumps(disabled_days_list),
        "min_day": min_date_formatted.strftime("%Y-%m-%d"),
        "min_day_number": min_day
    })


## API
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
            prod_db = Product.objects.filter(pk = product["id"]).first()
            
            if prod_db:
                try:
                    int(product["quantity"])
                    datetime.strptime(date, "%Y-%m-%d")
                    if int(product["quantity"]) < 1 or int(product["quantity"]) > 10:
                        raise Exception
                except:
                    return JsonResponse({'status': 'error', 'message': 'Something was wrong'}, status = 400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Something was wrong'}, status = 400)


            prod_db.quantity = int(product["quantity"])
            seller_user = prod_db.seller_user

            # Calculates total amount again
            ingredients = prod_db.ingredients.all()        
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
            delivery_date = date
        )

        order.save()

        for prod in products_db:
            OrderProduct.objects.create(
                product = prod,
                quantity = prod.quantity,
                order = order
            )

        return JsonResponse({'status': 'success', 'order_id': order.id})
    else:
        print('HERE!')
        print(json.loads(request.body))
        return JsonResponse({'status': 'error'}, status = 403)
    

