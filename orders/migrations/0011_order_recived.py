# Generated by Django 5.1.1 on 2024-10-31 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='recived',
            field=models.BooleanField(default=False),
        ),
    ]