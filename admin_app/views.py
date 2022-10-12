import calendar
import csv
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.template.loader import render_to_string
from accounts.models import Account
from admin_app.pdf import html_to_pdf
from brand.models import Brand
from carts.forms import CouponForm
from carts.models import Coupon
from category.models import Category
from orders.models import Order, OrderProduct, Payment
from product.models import Product
from brand.forms import BrandForm
from category.forms import CategoryForm
from product.forms import ProductForm
from store.forms import VariationForm
from store.models import Variation
from offer.forms import BrandOfferForm, CategoryOfferForm, ProductOfferForm
from offer.models import BrandOffer, CategoryOffer, ProductOffer


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if 'username' in request.session:
        return redirect(admin_home)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_superadmin == True:
            request.session['username'] = username
            login(request, user)
            return redirect(admin_home)

        else:
            messages.error(request, 'invalid credential')
            return redirect(admin_login)

    return render(request, 'admin/admin_login.html')


def admin_home(request):
    New = 0
    Accepted = 0
    Cancelled = 0
    Completed = 0
    Returned = 0

    if 'username' in request.session:
        income = 0
        orders = Order.objects.all()
        for order in orders:
            income += order.order_total
        income = int(income)
        labels = []
        data = []
        orders = OrderProduct.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(
            count=Count('id')).values('month', 'count')
        for d in orders:
            labels.append(calendar.month_name[d['month']])
            data.append([d['count']])
        labels1 = []
        data1 = []

        queryset = Order.objects.all()
        for i in queryset:
            if i.status == 'New':
                New += 1
            elif i.status == 'Accepted':
                Accepted += 1
            elif i.status == 'Cancelled':
                Cancelled += 1
            elif i.status == 'Completed':
                Completed += 1
            elif i.status == 'Returned':
                Returned += 1

        labels1 = ['New', 'Accepted', 'Cancelled', 'Completed', 'Returned']
        data1 = [New, Accepted, Cancelled, Completed, Returned]

        order_count = OrderProduct.objects.count()
        product_count = Product.objects.count()

        cat_count = Category.objects.count()
        user_count = Account.objects.count()

        category = Category.objects.all().order_by('-id')[:5]
        products = Product.objects.all().order_by('-id')[:5]
        orderproducts = OrderProduct.objects.all().order_by('-id')[:5]

        context = {
            'cat_count': cat_count,
            'product_count': product_count,
            'order_count': order_count,
            'labels1': labels1,
            'data1': data1,

            'labels': labels,
            'data': data,

            'category': category,
            'products': products,
            'orderproducts': orderproducts,
            'income': income,
            'user_count': user_count

        }
        return render(request, 'admin/admin_home.html', context)
    else:
        return redirect(admin_login)


def admin_logout(request):
    if 'username' in request.session:
        request.session.flush()
    logout(request)
    return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_list(request):
    if 'username' in request.session:
        search_key = request.GET.get('key') if request.GET.get('key') is not None else ''
        values = Category.objects.all().order_by('id') and Category.objects.filter(
            category_name__istartswith=search_key)
        p = Paginator(values, 4)
        page = request.GET.get('page')
        catvalues = p.get_page(page)

        return render(request, 'admin/categorylist.html', {'values': values, 'catvalues': catvalues})
    return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand_list(request):
    if 'username' in request.session:
        search_key = request.GET.get('key') if request.GET.get('key') is not None else ''
        values = Brand.objects.all().order_by('id') | Brand.objects.filter(brand_name__istartswith=search_key)
        p = Paginator(values, 4)
        page = request.GET.get('page')
        brandvalues = p.get_page(page)

        return render(request, 'admin/brandlist.html', {'values': values, 'brandvalues': brandvalues})

    return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_list(request):
    if 'username' in request.session:
        search_key = request.GET.get('key') if request.GET.get('key') is not None else ''
        values = Product.objects.all().order_by('id') and Product.objects.filter(
            Q(product_name__icontains=search_key) | Q(description__icontains=search_key))

        p = Paginator(values, 2)
        page = request.GET.get('page')
        productvalues = p.get_page(page)
        return render(request, 'admin/productlist.html', {'values': values, 'productvalues': productvalues})
    return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category(request):
    if 'username' in request.session:

        if request.method == "POST":
            cat_form = CategoryForm(request.POST, request.FILES)
            if cat_form.is_valid():
                cat_form.save()
                messages.success(request, 'Your category has been added sucessfully')
            else:
                messages.error(request, 'Error')

            return redirect(category_list)
        cat_form = CategoryForm()
        cats = Category.objects.all()
        context = {'cat_form': cat_form, 'cats': cats}
        return render(request, 'admin/addcategory.html', context)

    return redirect(admin_login)


def delete_category(request, id):
    if 'username' in request.session:
        my_cat = Category.objects.get(id=id)
        my_cat.delete()
        return redirect(category_list)
    else:
        return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_brand(request):
    if 'username' in request.session:

        if request.method == "POST":
            brand_form = BrandForm(request.POST, request.FILES)
            if brand_form.is_valid():
                brand_form.save()
                messages.success(request, 'Your brand has been added sucessfully')
            else:
                messages.error(request, 'Error')

            return redirect(brand_list)
        brand_form = BrandForm()
        brands = Brand.objects.all()
        context = {'brand_form': brand_form, 'brands': brands}
        return render(request, 'admin/addbrand.html', context)

    return redirect(admin_login)


def delete_brand(request, id):
    if 'username' in request.session:
        my_brand = Brand.objects.get(id=id)
        my_brand.delete()
        return redirect(brand_list)
    else:
        return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if 'username' in request.session:

        if request.method == "POST":
            prod_form = ProductForm(request.POST, request.FILES)
            if prod_form.is_valid():
                prod_form.save()
                messages.success(request, 'Your category has been added sucessfully')
            else:
                messages.error(request, 'Error')

            return redirect(product_list)
        prod_form = ProductForm()

        context = {'prod_form': prod_form}
        return render(request, 'admin/addproduct.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_product(request, id):
    if 'username' in request.session:
        product = Product.objects.get(id=id)
        form = ProductForm(instance=product)
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)

            if form.is_valid():
                form.save()
                return redirect(product_list)
        else:

            return render(request, 'admin/productedit.html', {'form': form})
    else:
        return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_category(request, id):
    if 'username' in request.session:
        category = Category.objects.get(id=id)
        form = CategoryForm(instance=category)
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES, instance=category)

            if form.is_valid():
                form.save()
                return redirect(category_list)
        else:

            return render(request, 'admin/categoryedit.html', {'form': form})
    else:
        return redirect(admin_login)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_brand(request, id):
    if 'username' in request.session:
        brand = Brand.objects.get(id=id)
        form = BrandForm(instance=brand)
        if request.method == 'POST':
            form = BrandForm(request.POST, request.FILES, instance=brand)

            if form.is_valid():
                form.save()
                return redirect(brand_list)
        else:

            return render(request, 'admin/brandedit.html', {'form': form})
    else:
        return redirect(admin_login)


def delete_product(request, id):
    if 'username' in request.session:
        my_product = Product.objects.get(id=id)
        my_product.delete()
        return redirect(product_list)
    else:
        return redirect(admin_login)


def active_users(request):
    if "key" in request.GET:
        search_key = request.GET.get('key') if request.GET.get('key') is not None else ''
        users = Account.objects.order_by("id").filter(is_admin=False).all() and Account.objects.filter(
            username__istartswith=search_key)
        context = {'users': users}
        return render(request, "admin/activeusers.html", context)
    else:
        users = Account.objects.order_by("id").filter(is_admin=False).all()
        context = {'users': users}
    return render(request, "admin/activeusers.html", context)


def block_user(request, user_id):
    if 'username' in request.session:
        user = Account.objects.get(pk=user_id)
        user.is_active = False
        user.save()
        return redirect("activeusers")


def unblock_user(request, user_id):
    if 'username' in request.session:
        user = Account.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        return redirect("activeusers")


def delete_user(request, user_id):
    if 'username' in request.session:
        dlt = Account.objects.get(pk=user_id)
        dlt.delete()
        return redirect("activeusers")


def order_display(request):
    if 'username' in request.session:
        if "key" in request.GET:
            search_key = request.GET.get('key') if request.GET.get('key') is not None else ''
            orders = Order.objects.order_by("id").filter(is_ordered=True).all() and Order.objects.filter(
                order_number__istartswith=search_key)
            context = {'orders': orders}
            return render(request, 'admin/orderadmin.html', context)
        else:
            order = Order.objects.filter(is_ordered=True).order_by('-id')
            orderproducts = OrderProduct.objects.all().order_by('-id')
            payment = Payment.objects.all()

            p = Paginator(order, 6)
            page = request.GET.get('page')
            orders = p.get_page(page)
            context = {
                'order': order,
                'orders': orders,
                'orderproducts': orderproducts,
                'payment': payment,

            }

            return render(request, 'admin/orderadmin.html', context)


    else:
        return redirect(admin_login)


def order_details_admin(request, id):
    if 'username' in request.session:

        orderproducts = OrderProduct.objects.filter(order=id).order_by('-id')
        return render(request, 'admin/orderdetailsadmin.html', {'orderproducts': orderproducts})

    else:
        return redirect(admin_login)


def order_status(request, id):
    if 'username' in request.session:
        if request.method == "POST":
            status = request.POST.get('status')

            order = Order.objects.get(id=id)
            order.status = status
            order.save()

        return redirect(order_display)

    else:
        return redirect(admin_login)


def view_coupon(request):
    if 'username' in request.session:
        values = Coupon.objects.all()
        return render(request, 'admin/couponlist.html', {'values': values})
    else:
        return redirect(admin_login)


def delete_coupon(request, id):
    if 'username' in request.session:
        my_coupon = Coupon.objects.get(id=id)
        my_coupon.delete()
        return redirect(view_coupon)
    else:
        return redirect(admin_login)


def add_coupon(request):
    if 'username' in request.session:

        if request.method == "POST":
            coupon_form = CouponForm(request.POST, request.FILES)
            if coupon_form.is_valid():
                coupon_form.save()
                messages.success(request, 'Your coupon has been added sucessfully')
            else:
                messages.error(request, 'Error')

            return redirect(view_coupon)
        coupon_form = CouponForm()

        context = {'coupon_form': coupon_form}
        return render(request, 'admin/addcoupon.html', context)

    return redirect(admin_login)


def variation(request):
    if 'username' in request.session:
        values = Variation.objects.all()
        return render(request, 'admin/variationlist.html', {'values': values})
    else:
        return redirect(admin_login)


def delete_variation(request, id):
    if 'username' in request.session:
        my_var = Variation.objects.get(id=id)
        my_var.delete()
        return redirect(variation)
    else:
        return redirect(admin_login)


def add_variation(request):
    if 'username' in request.session:

        if request.method == "POST":
            var_form = VariationForm(request.POST, request.FILES)
            if var_form.is_valid():
                var_form.save()
                messages.success(request, 'Your coupon has been added sucessfully')
            else:
                messages.error(request, 'Error')

            return redirect(variation)
        var_form = VariationForm()

        context = {'var_form': var_form}
        return render(request, 'admin/addvariation.html', context)

    return redirect(admin_login)


def brand_offer(request):
    offers = BrandOffer.objects.order_by("id").all()
    return render(
        request, "admin/existing_brand_Offer.html", {"offers": offers}
    )


def category_offer(request):
    offers = CategoryOffer.objects.order_by("id").all()
    return render(
        request, "admin/existing_category_Offer.html", {"offers": offers}
    )


def product_offer(request):
    offers = ProductOffer.objects.order_by("id").all()
    return render(
        request, "admin/existing_product_Offer.html", {"offers": offers}
    )


def add_brand_offer(request):
    form = BrandOfferForm()
    if request.method == "POST":
        form = BrandOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("brand_offer")
    context = {"form": form}
    return render(request, "admin/add_brand_offer.html", context)


def add_category_offer(request):
    form = CategoryOfferForm()
    if request.method == "POST":
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("category_offer")
    context = {"form": form}
    return render(request, "admin/add_category_offer.html", context)


def add_product_offer(request):
    form = ProductOfferForm()
    if request.method == "POST":
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_offer")
    context = {"form": form}
    return render(request, "admin/add_product_offer.html", context)


def block_brand_offer(request, brand_id):
    brandoff = BrandOffer.objects.get(pk=brand_id)
    brandoff.is_valid = False
    brandoff.save()
    return redirect("brand_offer")


def unblock_brand_offer(request, brand_id):
    brandoff = BrandOffer.objects.get(pk=brand_id)
    brandoff.is_valid = True
    brandoff.save()
    return redirect("brand_offer")


def block_category_offer(request, category_id):
    categoryoff = CategoryOffer.objects.get(pk=category_id)
    categoryoff.is_valid = False
    categoryoff.save()
    return redirect("category_offer")


def unblock_category_offer(request, category_id):
    categoryoff = CategoryOffer.objects.get(pk=category_id)
    categoryoff.is_valid = True
    categoryoff.save()
    return redirect("category_offer")


def block_product_offer(request, product_id):
    productoff = ProductOffer.objects.get(pk=product_id)
    productoff.is_valid = False
    productoff.save()
    return redirect("product_offer")


def unblock_product_offer(request, product_id):
    productoff = ProductOffer.objects.get(pk=product_id)
    productoff.is_valid = True
    productoff.save()
    return redirect("product_offer")


def delete_brand_offer(request, brand_id):
    dlt = BrandOffer.objects.get(pk=brand_id)
    dlt.delete()
    return redirect("brand_offer")


def delete_category_offer(request, category_id):
    dlt = CategoryOffer.objects.get(pk=category_id)
    dlt.delete()
    return redirect("category_offer")


def delete_product_offer(request, product_id):
    dlt = ProductOffer.objects.get(pk=product_id)
    dlt.delete()
    return redirect("product_offer")


def edit_brand_offer(request, brand_id):
    editBrandOff = BrandOffer.objects.get(pk=brand_id)
    form = BrandOfferForm(instance=editBrandOff)
    if request.method == "POST":
        form = BrandOfferForm(request.POST, instance=editBrandOff)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(request, "admin/editBrandOffer.html", context)
            return redirect("brand_offer")

    context = {"form": form}
    return render(request, "admin/editBrandOffer.html", context)


def edit_category_offer(request, category_id):
    editCategoryOff = CategoryOffer.objects.get(pk=category_id)
    form = CategoryOfferForm(instance=editCategoryOff)
    if request.method == "POST":
        form = CategoryOfferForm(request.POST, instance=editCategoryOff)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(
                    request, "admin/editCategoryOffer.html", context
                )
            return redirect("category_offer")

    context = {"form": form}
    return render(request, "admin/editCategoryOffer.html", context)


def edit_product_offer(request, product_id):
    editProductOff = ProductOffer.objects.get(pk=product_id)
    form = ProductOfferForm(instance=editProductOff)
    if request.method == "POST":
        form = ProductOfferForm(request.POST, instance=editProductOff)
        if form.is_valid():
            try:
                form.save()

            except:
                context = {"form": form}
                return render(request, "admin/editProductOffer.html", context)
            return redirect("product_offer")

    context = {"form": form}
    return render(request, "admin/editProductOffer.html", context)


def sales_report(request):
    product = Product.objects.all()
    context = {"product": product}
    return render(request, "admin/salesreport.html", context)





def sales_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=products.csv"

    writer = csv.writer(response)
    products = Product.objects.all().order_by("-id")

    writer.writerow(
        [

            "Product",
            "Brand",
            "Category",
            "Stock",
            "Price",
            "Sales Count",
            "Revenue",
            "Profit",

        ]
    )

    for product in products:
        writer.writerow(
            [

                product.product_name,
                product.brand,
                product.category,
                product.stock,
                product.price,
                product.get_count()[0]["quantity"],
                product.get_revenue()[0]["revenue"],
                product.get_profit(),

            ]
        )
    return response


def sales_export_pdf(request):
    product = Product.objects.all()
    open("templates/admin/pdf_out.html", "w").write(
        render_to_string("admin/sales_export_pdf.html", {"product": product}))
    pdf = html_to_pdf("admin/pdf_out.html")
    return HttpResponse(pdf, content_type="application/pdf")
