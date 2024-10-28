from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=60)
    image = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image
        }
    
    def __str__(self):
        return f"Category name: {self.name}, image: {self.image}"


class Ingredient(models.Model):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=550, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.FloatField()
    measurement_unit = models.CharField(max_length=30)
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seller_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ingredients")
    deleted_at = models.DateTimeField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "unit": self.size,
            "measurement_unit": self.measurement_unit,
            "availability": self.availability
        }
    
    def __str__(self):
        return f"The ingredient id: {self.id}, name: {self.name}, price: {self.price} - quantity: {self.size}{self.measurement_unit}, availability: {self.availability}"


class Product(models.Model):
    name = models.CharField(max_length=120)
    subtotal_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=500, null=True, blank=True)
    image = models.CharField(max_length=240, null=True, blank=True)
    production_time = models.IntegerField()
    seller_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name='products')
    deleted_at = models.DateTimeField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "subtotal_price": self.subtotal_price,
            "description": self.description,
            "image": self.image,
            "production_time": self.production_time,
            "seller_user": self.seller_user.username,
            "availability": self.availability,
            "categories": self.categories
        }
    
    def __str__(self):
        return f"The product id: {self.id}, name: {self.name}, total price: {self.subtotal_price}, seller: {self.seller_user}, availability: {self.availability}"

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="products")
    quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "ingredient": self.ingredient,
            "quantity": self.quantity,
            "created_at": self.created_at
        }

    def __str__(self):
        return f"The product {self.product.name} has the ingredient {self.ingredient.name} (quantity: {self.quantity})"

# class CategoryProduct(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='categories')
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
#     created_at = models.DateTimeField(auto_now_add=True)


