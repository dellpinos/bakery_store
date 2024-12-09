from django.test import Client, TestCase
from django.urls import reverse
from django.db.models import Max
from .models import Product, Category, Ingredient, ProductIngredient

from users.models import User

from orders.models import Cart, OrderProduct

class ProductTestCase (TestCase):
    
    def setUp(self):

        # Create Categories
        self.c1 = Category.objects.get(pk = 1)
        self.c2 = Category.objects.get(pk = 2)
        self.c3 = Category.objects.get(pk = 3)
        self.c4 = Category.objects.get(pk = 4)
        self.c5 = Category.objects.get(pk = 5)
        self.c6 = Category.objects.get(pk = 6)
        self.c7 = Category.objects.get(pk = 7)
        self.c8 = Category.objects.get(pk = 8)

        # Create User
        self.u1 = User.objects.create(
            username = 'usertest1',
            email = 'test01@test.com',
            password = 'securepassword123',
            first_name = 'Testino',
            last_name = 'Tester',
            is_active = True
        )

        self.u2 = User.objects.create(
            username = 'usertest2',
            email = 'test02@test.com',
            password = 'securepassword123',
            first_name = 'Testina',
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
            measurement_unit = 'kg',
            availability = True,
            seller_user = self.u1
        )

        self.i3 = Ingredient.objects.create(
            name = 'Sugar',
            description = '',
            price = 15,
            size = 2,
            measurement_unit = 'kg',
            availability = True,
            seller_user = self.u2
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
            name = 'Cake 2',
            subtotal_price = 80,
            description = 'Lorem ipsum',
            image = '',
            production_time = 3,
            seller_user = self.u1,
            availability = True
        )

        self.p3 = Product.objects.create(
            name = 'Cake 3',
            subtotal_price = 300,
            description = 'Lorem ipsum',
            image = '',
            production_time = 4,
            seller_user = self.u1,
            availability = False
        )

        self.p4 = Product.objects.create(
            name = 'Cake 4',
            subtotal_price = 3150,
            description = 'Lorem ipsum',
            image = '',
            production_time = 6,
            seller_user = self.u2,
            availability = True
        )

        self.p1.categories.add(self.c1, self.c2, self.c3)
        self.p2.categories.add(self.c1)
        self.p3.categories.add(self.c2, self.c3)
        self.p4.categories.add(self.c1, self.c3)
        
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
        self.pi7 = ProductIngredient.objects.create(
            product = self.p4,
            ingredient = self.i3,
            quantity = 0.2
        )


    # Test routes
    def test_home(self):

        """ Testing home view """
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].count(), 3)
        self.assertEqual(response.context["categories"].count(), 8)

    def test_home_filtered(self):

        """ Testing home filtered view """
        c = Client()

        response = c.get(f"/{self.c1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].count(), 3)
        self.assertEqual(response.context["categories"].count(), 8)

    def test_show_prod(self):
        
        """ Testing show product view """
        c = Client()
        p = self.p1
        response = c.get(reverse("show_product", kwargs={"product": p.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["related_products"]), 2)
        self.assertEqual(response.context["categories"].count(), 8)

    def test_show_prod_invalid_id(self):
        c = Client()
        p = Product.objects.order_by('-id').first()
        response = c.get(reverse("show_product", kwargs={"product": p.id + 1}))

        self.assertRedirects(response, reverse("index"))

    def test_show_random_prod(self):
        
        """ Testing show random product view """
        c = Client()
        response = c.get(reverse("random_product"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["related_products"]), 2)
        self.assertEqual(response.context["categories"].count(), 8)
