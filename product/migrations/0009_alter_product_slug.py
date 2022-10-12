# Generated by Django 4.1 on 2022-09-14 09:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_alter_product_images_alter_product_images1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=uuid.uuid1, max_length=100, unique=True),
        ),
    ]
