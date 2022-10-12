from django.contrib import admin

# Register your models here.
from store.models import Variation



class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ("is_active",)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')


admin.site.register(Variation, VariationAdmin)

