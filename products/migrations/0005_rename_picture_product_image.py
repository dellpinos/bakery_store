# Generated by Django 5.1.1 on 2024-09-12 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_ingredient_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='picture',
            new_name='image',
        ),
    ]
