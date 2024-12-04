from django.test import Client, TestCase
from django.urls import reverse
from django.db.models import Max
from .models import Product, Category, Ingredient, ProductIngredient

from users.models import User

from orders.models import Cart, OrderProduct

class ProductTestCase (TestCase):
    
    def setUp(self):

        # Create Categories
        c1 = Category.objects.get(pk = 1)
        c2 = Category.objects.get(pk = 2)
        c3 = Category.objects.get(pk = 3)
        c4 = Category.objects.get(pk = 4)
        c5 = Category.objects.get(pk = 5)
        c6 = Category.objects.get(pk = 6)
        c7 = Category.objects.get(pk = 7)
        c8 = Category.objects.get(pk = 8)

        # Create User
        self.u1 = User.objects.create(
            username = 'usertest1',
            email = 'test01@test.com',
            password = 'securepassword123',
            first_name = 'Testino',
            last_name = 'Tester',
            is_active = True
        )

        # Create Ingredients
        self.i1 = Ingredient.objects.create(
            name = 'Milk',
            description = '',
            price = 12,
            size = 3,
            measurement_unit = 'lt',
            availability = True,
            seller_user = self.u1
        )

        self.i2 = Ingredient.objects.create(
            name = 'Chocolate',
            description = '',
            price = 25,
            size = 1,
            measurement_unit = '',
            availability = True,
            seller_user = self.u1
        )

        # Create Products

        self.p1 = Product.objects.create(
            name = 'Cake 1',
            subtotal_price = 100,
            description = 'Lorem ipsum',
            image = '',
            production_time = 3,
            seller_user = self.u1,
            availability = True
        )

        self.p2 = Product.objects.create(
            name = 'Cake 1',
            subtotal_price = 80,
            description = 'Lorem ipsum',
            image = '',
            production_time = 3,
            seller_user = self.u1,
            availability = True
        )

        self.p3 = Product.objects.create(
            name = 'Cake 1',
            subtotal_price = 300,
            description = 'Lorem ipsum',
            image = '',
            production_time = 4,
            seller_user = self.u1,
            availability = False
        )

        self.p1.categories.add(c1, c2, c3)
        self.p2.categories.add(c1)
        self.p3.categories.add(c2, c3)
        
        self.pi1 = ProductIngredient.objects.create(
            product = self.p1,
            ingredient = self.i1,
            quantity = 1
        )
        self.pi2 = ProductIngredient.objects.create(
            product = self.p1,
            ingredient = self.i2,
            quantity = 0.4
        )
        self.pi3 = ProductIngredient.objects.create(
            product = self.p2,
            ingredient = self.i1,
            quantity = 1.2
        )
        self.pi4 = ProductIngredient.objects.create(
            product = self.p2,
            ingredient = self.i2,
            quantity = 0.3
        )
        self.pi5 = ProductIngredient.objects.create(
            product = self.p2,
            ingredient = self.i1,
            quantity = 1.1
        )
        self.pi6 = ProductIngredient.objects.create(
            product = self.p3,
            ingredient = self.i2,
            quantity = 0.3
        )


    # Test routes
    def test_home(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].count(), 2)
        self.assertEqual(response.context["categories"].count(), 8)

    def test_show_prod(self):
        c = Client()
        p = self.p1
        response = c.get(reverse("show_product", kwargs={"product": p.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["related_products"]), 1)
        self.assertEqual(response.context["categories"].count(), 8)


