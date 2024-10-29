
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("products.urls")),
    path('users/', include("users.urls")),
    path('dashboard/', include("dashboard.urls")),
    path('orders/', include("orders.urls"))
]