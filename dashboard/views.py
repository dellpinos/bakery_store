from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from products.models import Product, Category, Ingredient




@login_required
def index(request):

    return render(request, "dashboard/index.html")

@login_required
def all_products(request):

    products = Product.objects.filter(seller_user=request.user).order_by("-created_at")

    # Paginator
    p = Paginator(products, 20)

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, "dashboard/products.html", {
        "page": page
    })

@login_required
def all_ingredients(request):

    ingredients = Ingredient.objects.filter(seller_user=request.user).order_by("-created_at")

    # Paginator
    p = Paginator(ingredients, 20)

    if request.GET.get('page'):
        # Get the page number from the request
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page = p.page(page_number)

    return render(request, "dashboard/ingredients.html", {
        "page": page
    })




