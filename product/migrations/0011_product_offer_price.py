# Generated by Django 4.1 on 2022-10-08 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_productgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='offer_price',
            field=models.IntegerField(default=0),
        ),
    ]
