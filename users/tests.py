from django.test import Client, TestCase
from django.urls import reverse
from django.core import mail
from django.db.models import Max

from .models import User, Notification


class ProductTestCase (TestCase):
    
    def setUp(self):
        self.u1 = User.objects.create_user(
            username = 'usertest1',
            email = 'test01@test.com',
            password = 'securepassword123',
            first_name = 'Testino',
            last_name = 'Tester',
            is_active = True
        )

        self.u2 = User.objects.create_user(
            username = 'usertest2',
            email = 'test02@test.com',
            password = 'securepassword123',
            first_name = 'Testina',
            last_name = 'Tester',
            is_active = False
        )

    # Test routes
    def test_login(self):

        """ Testing login view """
        c = Client()
        response = c.get(reverse("login"))

        self.assertEqual(response.status_code, 200)


    def test_login_success(self):

        """ Testing login success """
        c = Client()

        response = c.post(reverse("login"), {
            "username": "usertest1",
            "password": "securepassword123"
        })
        # Redirige al dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))


    def test_login_fail(self):

        """ Testing login invalid user  """
        c = Client()
        
        response = c.post(reverse("login"), {
            "username": "usertest1",
            "password": "wrongpassword123"
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", c.session)


    def test_logout(self):

        """ Testing logout view """
        u = self.u1
        c = Client()
        c.force_login(u)

        self.assertTrue('_auth_user_id' in c.session)
        response = c.get(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn("_auth_user_id", c.session)

    def test_register(self):

        """ Testing register view """
        c = Client()
        response = c.get(reverse("register"))

        self.assertEqual(response.status_code, 200)

    def test_register_success(self):

        """ Testing register success """
        c = Client()

        response = c.post(reverse("register"), {
            "username": "newusertest",
            "email": "test@newtest.com",
            "password": "Securepassword123",
            "confirmation": "Securepassword123",
            "first_name": "First Tester",
            "last_name": "Last Tester"
        })

        # Verifies that the user was successfully created
        self.assertEqual(User.objects.count(), 3)
        user = User.objects.order_by('-id').first()
        self.assertEqual(user.username, "newusertest")
        self.assertFalse(user.is_active)  # User no activated

        # Checks redirection or message
        self.assertEqual(response.status_code, 200)
        self.assertIn("We have sent an email", response.content.decode())

        # Checks that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Activate your account", mail.outbox[0].subject)

    def test_register_duplicate_username(self):
        """Test registration fails if username is already taken """

        response = self.client.post(reverse("register"), {
            "username": "usertest1",
            "email": "test@newtest.com",
            "password": "SecurePassword123",
            "confirmation": "SecurePassword123",
            "first_name": "First Tester",
            "last_name": "Last Tester"
        })

        # Ensures that no additional user was created
        self.assertEqual(User.objects.count(), 2)

        # Verifies the error message
        self.assertEqual(response.status_code, 200)
        self.assertIn("Username already taken", response.content.decode())
