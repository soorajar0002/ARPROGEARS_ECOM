from django.urls import path, include

from user_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_register/', views.user_register, name='signup'),
    path("confirm_signup/", views.confirm_signup, name="confirm_signup"),
    path('user_logout/', views.user_logout, name='user_logout'),
    path("signinotp/", views.signin_otp, name="signinotp"),
    path("otpcheck/", views.otp_check, name="otpcheck"),
    path("resent_otp/", views.resent_otp, name="resent_otp"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("order_detail/<int:order_id>/", views.order_detail, name="order_detail"),
    path("canceled_order/", views.canceled_order, name="canceled_order"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("otp_reset_password/", views.otp_reset_password, name="otp_reset_password"),
    path("reset_password/", views.reset_password, name="reset_password"),

]
