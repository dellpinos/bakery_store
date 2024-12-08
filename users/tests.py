from django.test import Client, TestCase
from django.urls import reverse
from django.core import mail
from django.db.models import Max

from .models import User, Notification

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

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

    def test_login_fail_wrong_credentials(self):

        """ Testing login failure due to invalid credentials  """
        c = Client()
        
        response = c.post(reverse("login"), {
            "username": "usertest1",
            "password": "wrongpassword123"
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", c.session)

    def test_login_fail_no_activated(self):

        """ Testing login failure due no activated user  """
        c = Client()
        
        response = c.post(reverse("login"), {
            "username": "usertest2",
            "password": "securepassword123"
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


    def test_verify_email_success(self):
        
        """ Test successful email verification """
        uidb64 = urlsafe_base64_encode(force_bytes(self.u2.pk))
        token = default_token_generator.make_token(self.u2)
        url = reverse("verify_email", kwargs={"uidb64": uidb64, "token": token})

        client = Client()
        response = client.get(url)

        self.u2.refresh_from_db()  # Refresh DB
        self.assertTrue(self.u2.is_active)
        self.assertIn("_auth_user_id", client.session)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Your email has been successfully verified", response.content.decode())

    def test_verify_email_invalid_token(self):

        """ Test email verification with invalid token """
        uidb64 = urlsafe_base64_encode(force_bytes(self.u2.pk))
        token = "invalid-token"
        url = reverse("verify_email", kwargs={"uidb64": uidb64, "token": token})

        client = Client()
        response = client.get(url)

        self.u2.refresh_from_db()
        self.assertFalse(self.u2.is_active)
        self.assertNotIn("_auth_user_id", client.session)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Activation link is invalid", response.content.decode())

    def test_verify_email_user_not_found(self):

        """ Test email verification with non-existing user """
        uidb64 = urlsafe_base64_encode(force_bytes(9999))
        token = default_token_generator.make_token(self.u2)
        url = reverse("verify_email", kwargs={"uidb64": uidb64, "token": token})

        client = Client()
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Activation link is invalid", response.content.decode())

    def test_forgot_password_valid_email(self):

        """ Test sending reset email with valid email """
        client = Client()
        response = client.post(reverse("forgot_password"), {"email": self.u1.email})

        self.assertEqual(response.status_code, 200)
        self.assertIn("We have sent an email to your inbox", response.content.decode())
        self.assertEqual(len(mail.outbox), 1)  # Verificar que se envió un correo
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Reset your password")
        self.assertIn(self.u1.email, email.to)

    def test_forgot_password_invalid_email(self):

        """ Test sending reset email with invalid email """
        client = Client()
        response = client.post(reverse("forgot_password"), {"email": "nonexistent@example.com"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Email address is invalid", response.content.decode())
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_inactive_user(self):

        """ Test sending reset email for inactive user """
        client = Client()
        response = client.post(reverse("forgot_password"), {"email": self.u2.email})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Email address is invalid", response.content.decode())
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_get_request(self):

        """ Test accessing forgot password page via GET """
        client = Client()
        response = client.get(reverse("forgot_password"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/forgot_password.html")

    def test_valid_token(self):

        """ Test password verify email via GET """
        uidb64 = urlsafe_base64_encode(force_bytes(self.u2.pk))
        valid_token = default_token_generator.make_token(self.u2)
        response = self.client.get(reverse('password_verify_email', args=[uidb64, valid_token]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/reset_password.html')
        self.assertContains(response, uidb64)
        self.assertContains(response, valid_token)

    def test_invalid_token(self):

        """ Test password verify email with invalid password """
        invalid_token = 'invalid-token'
        uidb64 = urlsafe_base64_encode(force_bytes(self.u2.pk))
        response = self.client.get(reverse('password_verify_email', args=[uidb64, invalid_token]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/message.html')
        self.assertContains(response, "The reset password link is invalid or has expired")

    def test_invalid_uidb64(self):

        """ Test password verify email with invalid uidb64 """
        invalid_uidb64 = 'invalid-uidb64'
        valid_token = default_token_generator.make_token(self.u2)
        response = self.client.get(reverse('password_verify_email', args=[invalid_uidb64, valid_token]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/message.html')
        self.assertContains(response, "The reset password link is invalid or has expired")

    def test_passwords_must_match(self):
        
        """Test that an error is shown if passwords do not match"""
        uidb64 = urlsafe_base64_encode(force_bytes(self.u1.pk))
        valid_token = default_token_generator.make_token(self.u1)
        response = self.client.post(reverse("reset_password"), {
            "password": "bbBB1234",
            "confirmation": "ccCC1234",
            "email": self.u1.email,
            "uidb64": uidb64,
            "token": valid_token,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/reset_password.html")
        self.assertContains(response, "Passwords must match")

    def test_email_does_not_match(self):

        """Test that an error is shown if the email does not match the user"""
        uidb64 = urlsafe_base64_encode(force_bytes(self.u1.pk))
        valid_token = default_token_generator.make_token(self.u1)
        response = self.client.post(reverse("reset_password"), {
            "password": "bbBB1234",
            "confirmation": "bbBB1234",
            "email": "wrong@example.com",
            "uidb64": uidb64,
            "token": valid_token,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/reset_password.html")
        self.assertContains(response, "The email address does not match")

    def test_successful_password_reset(self):

        """Test that the password is successfully reset with valid data"""
        uidb64 = urlsafe_base64_encode(force_bytes(self.u1.pk))
        valid_token = default_token_generator.make_token(self.u1)
        response = self.client.post(reverse("reset_password"), {
            "password": "bbBB1234",
            "confirmation": "bbBB1234",
            "email": self.u1.email,
            "uidb64": uidb64,
            "token": valid_token,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/login.html")
        self.assertContains(response, "Password updated")
        self.u1.refresh_from_db()
        self.assertTrue(self.u1.check_password("bbBB1234"))