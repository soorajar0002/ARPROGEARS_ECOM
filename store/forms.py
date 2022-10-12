from django import forms
from .models import Variation


class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = (
            'product', 'variation_category', 'variation_value', 'is_active')
