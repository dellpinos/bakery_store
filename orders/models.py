from django.db import models
from users.models import User
from products.models import Product


class Order(models.Model):
    buyer_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "buyer_orders")
    seller_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "seller_orders")
    total_amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    delivery_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default = False)

    def serialize(self):
        return {
            "buyer_user": self.buyer_user,
            "total_amount": self.total_amount,
            "delivery_date": self.delivery_date
        }
    def __str__(self):
        return f"Id: {self.id}, Total: ${self.total_amount}, Delivery at: {self.delivery_date}"


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "orders")
    quantity = models.IntegerField( default = 1 )
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name = "products")
    created_at = models.DateTimeField(auto_now_add = True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def serialize(self):
        return {
            "product": self.product,
            "quantity": self.quantity,
            "order": self.order
        }
    def __str__(self):
        return f"Id: {self.id}, Product: {self.product.id}, Quantity: {self.quantity}, Order: {self.order.id}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "cart")

    def serialize(self):
        return {
            "user": self.user,
            "products": self.products
        }
    def __str__(self):
        return f"{self.user}'s cart"

class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "carts")
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name = "products")
    quantity = models.IntegerField( default = 1 )
    created_at = models.DateTimeField(auto_now_add = True)

    def serialize(self):
        return {
            "product": self.product,
            "cart": self.cart,
            "quantity": self.quantity,
            "created_at": self.created_at
        }
    def __str__(self):
        return f"Product: {self.product}, quantity: {self.quantity}. User: {self.cart.user}"
