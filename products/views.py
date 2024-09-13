from django.shortcuts import render
from .models import Product

def home(request):

    products = Product.objects.order_by('-created_at')
    return render(request, "home/index.html", {
        "products": products
    })
