from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('verify_email/<uidb64>/<token>/', views.verify_email, name='verify_email'),


    path('password_verify_email/<uidb64>/<token>/', views.password_verify_email, name='password_verify_email'),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('reset_password/', views.reset_password, name='reset_password'),


    # API
    path('api/notifications/', views.get_notifications, name="get_notifications"),
    path('api/notification_delete/<int:id>/', views.delete_notification, name="delete_notification"),
    path('api/mark_read/<int:id>/', views.mark_read_notification, name="mark_read_notification"),

]