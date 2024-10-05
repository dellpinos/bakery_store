from django.db import models
from users.models import User
from products.models import Product


class Order(models.Model):
    buyer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "buyer_user": self.buyer_user,
            "total_amount": self.total_amount,
            "deliver_date": self.delivery_date
        }
    def __str__(self):
        return f"Id: {self.id}, Total: ${self.total_amount}, Delivery at: {self.delivery_date}"


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="products") 
    created_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    products = models.ManyToManyField(Product, related_name='carts')

    def serialize(self):
        return {
            "user": self.user,
            "products": self.products
        }
    def __str__(self):
        return f"{self.user}'s cart"

