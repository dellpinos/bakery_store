from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='index'),
    path('new_product/', views.new_product, name="new_product"),
    path('new_ingredient/', views.new_ingredient, name="new_ingredient"),
    path('edit_ingredient/<int:ingredient>', views.edit_ingredient, name="edit_ingredient"),
]

