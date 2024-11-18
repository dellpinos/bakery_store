from django.contrib import admin

from .models import User, SellerTimeOff, Notification

admin.site.register(User)
admin.site.register(SellerTimeOff)
admin.site.register(Notification)
