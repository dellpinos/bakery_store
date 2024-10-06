from django.contrib import admin
from .models import Order, OrderProduct, Cart


admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Cart)
