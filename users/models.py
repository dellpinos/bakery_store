from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    def __str__(self):
        return f"Id: {self.id} - Username: {self.username}, Email: {self.email}"
    
class SellerTimeOff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='days_off')
    date = models.DateField()

    def serialize(self):
        return {
            "user": self.user,
            "date": self.date
        }
    
    def __str__(self):
        return f"The user: {self.user} is free on date: {self.date}"