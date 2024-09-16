from django.contrib import admin
from .models import Product, Category, Ingredient

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Ingredient)