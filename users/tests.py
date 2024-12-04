from django.test import Client, TestCase
from django.db.models import Max
from .models import User, Notification


class ProductTestCase (TestCase):
    
    def setUp(self):
        u1 = User.objects.create(
            username = 'usertest1',
            email = 'test01@test.com',
            password = 'securepassword123',
            first_name = 'Testino',
            last_name = 'Tester',
            is_active = True
        )

        u2 = User.objects.create(
            username = 'usertest2',
            email = 'test02@test.com',
            password = 'securepassword123',
            first_name = 'Testina',
            last_name = 'Tester',
            is_active = True
        )
