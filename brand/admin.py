from django.contrib import admin
from .models import Brand


# Register your models here.


class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'slug', )
    prepopulated_fields = {'slug': ('brand_name',)}


admin.site.register(Brand, BrandAdmin)
