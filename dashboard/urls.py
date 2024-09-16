from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='dashboard'),
    path('products/', views.all_products, name="dashboard_products"),
    path('new_product/', views.new_product, name="new_product"),
]

