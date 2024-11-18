from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('products/', views.all_products, name="dashboard_products"),
    path('ingredients/', views.all_ingredients, name="dashboard_ingredients"),
    path('settings/', views.settings, name="dashboard_settings"),
    path('calendar_update/', views.calendar_update, name="calendar_update"),
    path('capacity_update/', views.capacity_update, name="capacity_update"),
    path('disable_all/', views.disable_all, name="disable_all"),

    ## API
    path('api/calendar_info/<int:quantity>/<int:user>/', views.check_dates, name="calendar_info"),
]