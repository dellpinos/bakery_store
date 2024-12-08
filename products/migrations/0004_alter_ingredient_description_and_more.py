# Generated by Django 5.1.1 on 2024-09-12 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_rename_porductingredient_productingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='description',
            field=models.CharField(blank=True, max_length=550, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='picture',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
