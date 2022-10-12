from django import forms
from .models import Coupon, UsedCoupon


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = (
            'coupon_code', 'discount', 'is_active')


class UsedCouponForm(forms.ModelForm):
    class Meta:
        model = UsedCoupon
        fields = (
            'user', 'coupon')

