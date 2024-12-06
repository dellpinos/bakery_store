from django.test import Client, TestCase
from django.core.paginator import Page
from django.urls import reverse
from django.db.models import Max

from products.models import Product, Category, Ingredient, ProductIngredient
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
    def test_dashboard_valid_user(self):

        """ Testng dashboard with no authorized user """
        u = self.u1
        c = Client()
        c.force_login(u)

        response = c.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_invalid_user(self):

        """ Testng dashboard with no authorized user """
        c = Client()
        response = c.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_all_products(self):

        """ Testng dashboard all products with authorized user """
        u = self.u1
        c = Client()
        c.force_login(u)

        response = c.get(reverse("dashboard_products"))

        # Get page from the context
        page: Page = response.context["page"]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(page.object_list), 3)

    def test_dashboard_all_products_invalid_user(self):

        """ Testng dashboard all products with no authorized user """
        c = Client()
        response = c.get(reverse("dashboard_products"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_all_ingredients(self):

        """ Testng dashboard all ingredients with authorized user """
        u = self.u1
        c = Client()
        c.force_login(u)

        response = c.get(reverse("dashboard_ingredients"))

        # Get page from the context
        page: Page = response.context["page"]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(page.object_list), 2)

    def test_dashboard_all_ingredients_invalid_user(self):

        """ Testng dashboard all ingredients with no authorized user """
        c = Client()
        response = c.get(reverse("dashboard_ingredients"))
        self.assertEqual(response.status_code, 302)


    def test_dashboard_settings(self):

        """ Testng dashboard settings with authorized user """
        u = self.u1
        c = Client()
        c.force_login(u)

        response = c.get(reverse("dashboard_settings"))

        # Validates context keys
        context = response.context
        self.assertIn("days_off", context)
        self.assertIn("pending_dates", context)
        self.assertIn("capacity", context)

        # Validates context content
        self.assertTrue(context["days_off"])
        self.assertTrue(context["pending_dates"])
        self.assertTrue(context["capacity"])
        
        self.assertEqual(response.status_code, 200)


    def test_dashboard_settings_invalid_user(self):

        """ Testng dashboard settings with no authorized user """
        c = Client()
        response = c.get(reverse("dashboard_settings"))
        self.assertEqual(response.status_code, 302)