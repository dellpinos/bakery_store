from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    # API
    path('api/notifications/', views.get_notifications, name="get_notifications"),
    path('api/notification_delete/<int:id>', views.delete_notification, name="delete_notification"),
    path('api/mark_read/<int:id>', views.mark_read_notification, name="mark_read_notification"),

]