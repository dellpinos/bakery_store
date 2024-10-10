from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path('checkout', views.checkout, name="checkout"),

    # API
    path('api/cart/', views.index_cart, name="index_cart"),
    path('api/cart/create/<int:product>', views.create_cart, name="create_cart"),



    
]