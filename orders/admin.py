from django.contrib import admin
from .models import Order, OrderProduct, Cart, CartProduct


admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Cart)
admin.site.register(CartProduct)

