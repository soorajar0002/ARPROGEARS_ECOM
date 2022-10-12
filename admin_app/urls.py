from django.urls import path, include

from admin_app import views

urlpatterns = [

    path('', views.admin_home, name='adminhome'),
    path('adminlogout', views.admin_logout, name='adminlogout'),
    path('adminlogin', views.admin_login, name='adminlogin'),

    # Category
    path('admincategory', views.categoryList, name='categorylist'),
    path('addadmincategory', views.addcategory, name='addcategory'),
    path('editcategory/<int:id>', views.editcategory, name='edit-category'),
    path('deletecategory/<int:id>', views.deletecategory, name='delete-category'),

    # Brand
    path('adminbrand', views.brandList, name='brandlist'),
    path('addadminbrand', views.addbrand, name='addbrand'),
    path('deletebrand/<int:id>', views.deletebrand, name='delete-brand'),
    path('editbrand/<int:id>', views.editbrand, name='edit-brand'),

    # Product
    path('adminproduct', views.productList, name='productlist'),
    path('addadminproduct', views.addproduct, name='addproduct'),
    path('deleteproduct/<int:id>', views.deleteproduct, name='delete-product'),
    path('editproduct/<int:id>', views.editproduct, name='edit-product'),

    # Brand Offer
    path('brand_offer', views.brand_Offer, name='brand_offer'),
    path('add_brand_offer', views.add_brand_offer, name='add_brand_offer'),
    path("blockBrandOffer/<brand_id>", views.blockBrandOffer, name="blockBrandOffer"),
    path("unblockBrandOffer/<brand_id>", views.unblockBrandOffer, name="unblockBrandOffer"),
    path("deleteBrandOffer/<brand_id>", views.deleteBrandOffer, name="deleteBrandOffer"),
    path("editBrandOffer/<brand_id>", views.editBrandOffer, name="editBrandOffer"),

    # Category Offer
    path('category_offer', views.category_Offer, name='category_offer'),
    path('add_category_offer', views.add_category_offer, name='add_category_offer'),
    path("blockCategoryOffer/<category_id>", views.blockCategoryOffer, name="blockCategoryOffer"),
    path("unblockCategoryOffer/<category_id>", views.unblockCategoryOffer, name="unblockCategoryOffer"),
    path("deleteCategoryOffer/<category_id>", views.deleteCategoryOffer, name="deleteCategoryOffer"),
    path("editCategoryOffer/<category_id>", views.editCategoryOffer, name="editCategoryOffer"),

    # Product Offer
    path('product_offer', views.product_Offer, name='product_offer'),
    path('add_product_offer', views.add_product_offer, name='add_product_offer'),
    path("blockProductOffer/<product_id>", views.blockProductOffer, name="blockProductOffer"),
    path("unblockProductOffer/<product_id>", views.unblockProductOffer, name="unblockProductOffer"),
    path("deleteProductOffer/<product_id>", views.deleteProductOffer, name="deleteProductOffer"),
    path("editProductOffer/<product_id>", views.editProductOffer, name="editProductOffer"),

    # Sales Report
    path('sales_report', views.sales_report, name='sales_report'),
    path("sales_export_csv", views.sales_export_csv, name="sales_export_csv"),
    path("sales_export_pdf", views.sales_export_pdf, name="sales_export_pdf"),

    # Coupon
    path("viewcoupon", views.viewcoupon, name="viewcoupon"),
    path('addadmincoupon', views.addcoupon, name='addcoupon'),
    path('deletecoupon/<int:id>', views.deletecoupon, name='delete-coupon'),

    # Variation
    path("variation", views.variation, name="variation"),
    path('addvariation', views.addvariation, name='addvariation'),
    path("deletevariation/<int:id>", views.deletevariation, name="deletevariation"),

    # User
    path("activeusers", views.activeusers, name="activeusers"),
    path("blockuser/<user_id>", views.blockuser, name="blockuser"),
    path("unblockuser/<user_id>", views.unblockuser, name="unblockuser"),
    path("deleteuser/<user_id>", views.deleteuser, name="deleteuser"),

    # Order
    path("orderdisplay/", views.orderdisplay, name="orderdisplay"),
    path('orderdetailsadmin/<int:id>/', views.orderdetailsadmin, name='orderdetailsadmin'),
    path('orderstatus/<int:id>/', views.orderstatus, name='orderstatus'),

]
