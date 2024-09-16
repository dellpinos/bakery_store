from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from products.models import Product, Category, Ingredient




@login_required
def index(request):

    return render(request, "dashboard/index.html")

@login_required
def all_products(request):

    products = Product.objects.filter(seller_user=request.user).order_by("-created_at")

    return render(request, "dashboard/products.html", {
        "products": products
    })

@login_required
def new_product(request):

    if request.method == 'POST':
        pass
    else:

        categories = Category.objects.all()
        ingredients = Ingredient.objects.filter(seller_user=request.user).order_by("name")
        
        return render(request, "dashboard/create_product.html", {
            "categories": categories,
            "ingredients": ingredients
        })