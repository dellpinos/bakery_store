from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path('checkout/', views.checkout, name="checkout"),
    path('pending/orders/', views.pending_orders, name="pending_orders"),
    path('pending_deliveries/', views.pending_deliveries, name="pending_deliveries"),

    # API
    path('api/cart/', views.index_cart, name="index_cart"),
    path('api/cart/create/<int:product>/', views.create_cart, name="create_cart"),
    path('api/cart/item_delete/<int:product>/', views.delete_cart_item, name="cart_item_delete"),
    path('api/order/create/', views.create_order, name="create_order"),
    path('api/order/delete/<int:order>/', views.delete_order, name="delete_order"),
    path('api/order/confirm/<int:order>/', views.confirm_order, name="confirm_order")

]