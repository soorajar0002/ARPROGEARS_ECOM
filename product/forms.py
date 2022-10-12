from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'product_name', 'slug', 'description', 'price', 'images', 'images1', 'images2', 'is_available', 'stock', 'category','brand')
