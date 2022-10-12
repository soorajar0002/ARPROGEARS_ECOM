import datetime
import json

import razorpay
from decouple import config
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from razorpay import client

from product.models import Product
from django.shortcuts import render, redirect
from carts.models import CartItem, Coupon, UsedCoupon
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderProduct
from django.http import JsonResponse

client = razorpay.Client(auth=(config('RAZOR_KEY_ID'), config('RAZOR_KEY_SECRET')))


def payments(request):
    body = json.loads(request.body)

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        if item.product.Offer_Price():
            offer_price = Product.Offer_Price(item.product)
            price = offer_price["new_price"]
            orderproduct.product_price = price
        else:
            orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,

    }

    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    tax = 0
    if 'coupon_code' in request.session:

        coupon = Coupon.objects.get(coupon_code=request.session['coupon_code'])
        reduction = coupon.discount

    else:
        reduction = 0
    for cart_item in cart_items:
        if cart_item.product.Offer_Price():
            offer_price = Product.Offer_Price(cart_item.product)
            print(offer_price["new_price"])
            total = total + (
                    offer_price["new_price"] * cart_item.quantity
            )
            print(total)
        else:
            total = total + (cart_item.product.price * cart_item.quantity)

        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax - reduction

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.discount = reduction
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")

            currency = "INR"
            amount = grand_total * 100
            request.session["razorpay_amount"] = amount
            razorpay_order = client.order.create(
                dict(amount=amount, currency=currency, payment_capture="0")
            )
            order_number = current_date + str(data.id)
            data.order_number = order_number
            request.session["order_number"] = order_number
            data.save()

            razorpay_order_id = razorpay_order["id"]
            callback_url = "paymenthandler/"

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                "razorpay_order_id": razorpay_order_id,
                "razorpay_merchant_key": settings.RAZOR_KEY_ID,
                "razorpay_amount": amount,
                "currency": currency,
                "callback_url": callback_url,

            }

            return render(request, 'store/payments.html', context)
        else:
            return redirect('checkout')


def payment_method(request):
    request.session["payment_method"] = "razor_pay"
    return redirect("place_order")


@csrf_exempt
def paymenthandler(request, total=0, quantity=0):
    if request.method == "POST":
        try:

            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            print("hello")
            print(payment_id, "razorpay_payment_id")
            print(razorpay_order_id)

            result = client.utility.verify_payment_signature(
                params_dict
            )
            if result is None:

                amount = request.session["razorpay_amount"]
                try:

                    client.payment.capture(payment_id, amount)

                    current_user = request.user
                    order = Order.objects.get(
                        user=current_user,
                        is_ordered=False,
                        order_number=razorpay_order_id,
                    )

                    payment = Payment(
                        user=current_user,
                        payment_id=payment_id,
                        payment_method="RazorPay",
                        amount_paid=order.order_total,
                        status="Completed",
                    )
                    payment.save()
                    order.user = current_user
                    order.payment = payment
                    order.is_ordered = True
                    order.save()

                    cart_items = CartItem.objects.filter(
                        user=current_user
                    )

                    for item in cart_items:
                        orderproduct = OrderProduct()
                        orderproduct.order_id = order.id
                        orderproduct.payment = payment
                        orderproduct.user_id = request.user.id
                        orderproduct.product_id = item.product_id
                        orderproduct.quantity = item.quantity
                        if item.product.Offer_Price():
                            offer_price = Product.Offer_Price(
                                item.product
                            )
                            price = offer_price["new_price"]
                            orderproduct.product_price = price
                        else:
                            orderproduct.product_price = (
                                item.product.price
                            )
                        orderproduct.ordered = True
                        orderproduct.save()

                        cart_item = CartItem.objects.get(id=item.id)
                        product_variation = cart_item.variations.all()
                        orderproduct = OrderProduct.objects.get(
                            id=orderproduct.id
                        )
                        orderproduct.variations.set(product_variation)
                        orderproduct.save()

                        # reduce the quantity of sold products
                        product = Product.objects.get(id=item.product_id)
                        product.stock = product.stock - item.quantity
                        product.save()

                        # clear the cart
                        CartItem.objects.filter(
                            user=request.user
                        ).delete()

                    param = (
                            "order_number="
                            + order.order_number
                            + "&payment_id="
                            + payment.payment_id
                    )
                    ################
                    # capture the payemt
                    messages.success(request, "Payment Success")

                    redirect_url = reverse("order_complete")
                    return redirect(f"{redirect_url}?{param}")

                except Exception as e:
                    print(e)
                    messages.error(request, "Payment is Failed")
                    # if there is an error while capturing payment.
                    return redirect("place_order")
            else:

                return redirect("place_order")
                # if signature verification fails.

        except:
            return redirect("place_order")
            # if we don't find the required parameters in POST data
    else:
        # if other than POST request is made.
        return redirect("place_order")


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        payment = Payment.objects.get(payment_id=transID)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,

        }

        return render(request, 'store/order_complete.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')


def cod(request):
    current_user = request.user

    order_number = request.session["order_number"]
    print(order_number)

    order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
    print(order)

    payment = Payment(
        user=current_user,
        payment_id=order_number,
        payment_method="Cash On Delivery",
        amount_paid=order.order_total,
        status="Payment Pending",
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        if item.product.Offer_Price():
            offer_price = Product.Offer_Price(item.product)
            price = offer_price["new_price"]
            orderproduct.product_price = price
        else:
            orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    param = (
            "order_number="
            + order.order_number
            + "&payment_id="
            + payment.payment_id
    )

    messages.success(request, "Payment Success")
    if "order_number" in request.session:
        del request.session["order_number"]

    redirect_url = reverse("order_complete")
    return redirect(f"{redirect_url}?{param}")


def cancel_order(request, order_id):
    order = Order.objects.get(order_number=order_id)
    order.is_ordered = False
    order.status = "Cancelled"
    order.save()

    return redirect('my_orders')


def return_order(request, order_id):
    order = Order.objects.get(order_number=order_id)
    order.is_ordered = True
    order.status = "Returned"
    order.payment.status = "Refunded"
    order.payment.save()
    order.save()

    return redirect('my_orders')


def orderstatus(request, id):
    if request.method == "POST":
        status = request.POST.get('status')

        order = Order.objects.get(id=id)
        if status == "Cancelled":
            order.is_ordered = False

        order.status = status
        order.save()

    return redirect('orderdisplay')
