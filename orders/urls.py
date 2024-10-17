from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path('checkout', views.checkout, name="checkout"),

    # API
    path('api/cart/', views.index_cart, name="index_cart"),
    path('api/cart/create/<int:product>', views.create_cart, name="create_cart"),
    path('api/cart/item_delete/<int:product>', views.delete_cart_item, name="cart_item_delete"),
    path('api/order/create', views.create_order, name="create_order"),

]