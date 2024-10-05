from django.urls import path
from . import views


urlpatterns = [
    # Public
    path('', views.home, name='index'),
    path('show_product/<int:product>', views.show_product, name="show_product"),

    # Dashboard
    path('new_product/', views.new_product, name="new_product"),
    path('edit_product/<int:product>', views.edit_product, name="edit_product"),
    path('random_product', views.random_product, name="random_product"),
    path('new_ingredient/', views.new_ingredient, name="new_ingredient"),
    path('edit_ingredient/<int:ingredient>', views.edit_ingredient, name="edit_ingredient"),
    path('delete_ingredient/<int:ingredient>', views.delete_ingredient, name="delete_ingredient"),

    # API
    path('api/ingredient_availability/<int:ingredient>', views.ingredient_availability, name="ingredient_availability"),
    path('api/product_availability/<int:product>', views.product_availability, name="product_availability")
]

