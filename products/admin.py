from django.contrib import admin
from .models import Product, Category, Ingredient, ProductIngredient

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(ProductIngredient)