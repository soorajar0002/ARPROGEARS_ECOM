from django.db import models


# Create your models here.
class Brand(models.Model):
    brand_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    brand_logo = models.ImageField(upload_to='photos/brands')

    def __str__(self):
        return self.brand_name


class ModelAdmin:
    pass
