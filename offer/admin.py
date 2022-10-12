from django.contrib import admin

# Register your models here.
from offer.models import BrandOffer, CategoryOffer, ProductOffer

admin.site.register(BrandOffer)
admin.site.register(CategoryOffer)
admin.site.register(ProductOffer)