# Generated by Django 5.1.1 on 2024-10-22 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
