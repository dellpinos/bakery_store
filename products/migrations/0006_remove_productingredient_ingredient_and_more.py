# Generated by Django 5.1.1 on 2024-09-16 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_rename_picture_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='productingredient',
            name='product',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='unit_measure',
            field=models.CharField(default='kg', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='availability',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(related_name='products', to='products.category'),
        ),
        migrations.AddField(
            model_name='product',
            name='ingredients',
            field=models.ManyToManyField(related_name='products', to='products.ingredient'),
        ),
        migrations.DeleteModel(
            name='CategoryProduct',
        ),
        migrations.DeleteModel(
            name='ProductIngredient',
        ),
    ]
