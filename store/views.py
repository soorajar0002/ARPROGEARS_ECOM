from django.db.models import Q

from django.shortcuts import render, get_object_or_404

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from product.models import Product, ProductGallery

from django.core.paginator import Paginator


# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)

        products = Product.objects.filter(category=categories, is_available=True)
        for product in products:
            if product.Offer_Price():
                new = Product.Offer_Price(product)
                product.offer_price = new["new_price"]
                product.percentage = new["discount"]
                product.save()
            else:
                product.offer_price = 0
                product.save()

        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:

        products = Product.objects.all().filter(is_available=True).order_by('id')
        for product in products:
            if product.Offer_Price():
                new = Product.Offer_Price(product)
                product.offer_price = new["new_price"]
                product.percentage = new["discount"]
                print(product.offer_price)
                product.save()
            else:
                product.offer_price = 0
                print(product.offer_price)
                product.save()


        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()


    except Exception as e:
        raise e
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'product_gallery': product_gallery,
    }

    return render(request, 'store/productdetail.html', context)


def search(request):
    if "key" in request.GET:
        keyword = request.GET["key"]
        if keyword:
            products = Product.objects.order_by("id").filter(
                Q(description__icontains=keyword)
                | Q(product_name__icontains=keyword)
            )

            # q means query set
            product_count = products.count()

    context = {
        "products": products,
        "product_count": product_count,

    }
    return render(request, "store/store.html", context)
