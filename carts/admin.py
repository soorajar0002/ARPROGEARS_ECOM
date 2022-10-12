from django.contrib import admin
from .models import Cart, CartItem, Coupon, UsedCoupon


# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity')


class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'discount', 'is_active')


class UsedCouponAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon')


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(UsedCoupon, UsedCouponAdmin)
