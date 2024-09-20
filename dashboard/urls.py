from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='dashboard'),
    path('products/', views.all_products, name="dashboard_products"),
    path('ingredients/', views.all_ingredients, name="dashboard_ingredients")

]

