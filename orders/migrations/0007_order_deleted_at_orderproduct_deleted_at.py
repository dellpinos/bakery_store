# Generated by Django 5.1.1 on 2024-10-18 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_seller_user_alter_order_buyer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
