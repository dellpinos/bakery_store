# Generated by Django 5.1.1 on 2024-10-10 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='max_prod_capacity',
            field=models.IntegerField(default=3),
        ),
    ]