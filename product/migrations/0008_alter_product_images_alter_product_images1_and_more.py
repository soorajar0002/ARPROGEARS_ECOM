# Generated by Django 4.1 on 2022-09-14 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_alter_product_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ImageField(upload_to='photos/products'),
        ),
        migrations.AlterField(
            model_name='product',
            name='images1',
            field=models.ImageField(upload_to='photos/products'),
        ),
        migrations.AlterField(
            model_name='product',
            name='images2',
            field=models.ImageField(upload_to='photos/products'),
        ),
    ]