from django.contrib import messages, auth
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Account, UserProfile
from product.models import Product
from django.contrib.auth.decorators import login_required
from user_app.forms import RegistrationForm
from accounts.forms import UserForm, UserProfileForm
from user_app.otp import sentOTP, checkOTP
from orders.models import Order, OrderProduct
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests


def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products': products,
    }
    return render(request, 'user/home.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None and user.is_active == True:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)

                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()




            except:
                pass
            auth.login(request, user)
            request.session['email'] = email
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('home')
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('user_login')
    else:
        return render(request, 'user/userlogin.html')


def user_logout(request):
    auth.logout(request)
    return redirect('home')


def user_register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            request.session["first_name"] = first_name
            request.session["last_name"] = last_name
            request.session["email"] = email
            request.session["checkmobile"] = phone_number
            request.session["password"] = password
            request.session["username"] = username
            sentOTP(phone_number)
            return redirect("confirm_signup")
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "user/userregister.html", context)


def confirm_signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        otp = request.POST["otpcode"]
        phone_number = request.session["checkmobile"]
        print(otp)
        if checkOTP(phone_number, otp):
            first_name = request.session["first_name"]
            last_name = request.session["last_name"]
            email = request.session["email"]
            phone_number = request.session["checkmobile"]
            password = request.session["password"]
            username = request.session["username"]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username,

            )
            user.is_active = True
            user.phone_number = phone_number
            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = "default/avatar.png"
            profile.save()
            user.save()
            messages.success(request, "Registered successfully")
            return redirect("user_login")
        else:
            print("OTP not matching")
            return redirect("confirm_signup")
    return render(request, "user/confirm_signup.html")


def signin_otp(request):
    if request.method == "POST":
        mobile = request.POST["phone"]
        try:
            if Account.objects.get(phone_number=mobile):
                sentOTP(mobile)
                request.session["checkmobile"] = mobile
                return redirect("otpcheck")
        except:
            messages.info(request, "User not registered")
            return redirect("signinotp")
    return render(request, "user/signinotp.html")


def otpcheck(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        otp = request.POST["otpcode"]
        mobile = request.session["checkmobile"]
        a = checkOTP(mobile, otp)
        if a:
            user = Account.objects.get(phone_number=mobile)
            auth.login(request, user)
            messages.info(request, "Autheticated Successfully")
            return redirect("home")

        else:
            messages.info(request, "OTP not Valid")
            return redirect("otpcheck")

    return render(request, "user/otpcheck.html")


def resent_otp(request):
    mobile = request.session["checkmobile"]
    sentOTP(mobile)
    return redirect("otpcheck")


@login_required(login_url='user_login')
def dashboard(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,

    }
    return render(request, 'user/dashboard.html', context)


@login_required(login_url='user_login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,

    }
    return render(request, 'user/my_orders.html', context)


@login_required(login_url='user_login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0

    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'user/order_detail.html', context)


@login_required(login_url='user_login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile
    }
    return render(request, 'user/edit_profile.html', context)


@login_required(login_url='user_login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match')
            return redirect('change_password')

    return render(request, 'user/change_password.html')


def canceled_order(request):
    orders = Order.objects.filter(user=request.user, is_ordered=False).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'user/cancelled_orders.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        user = Account.objects.get(phone_number=phone_number, email=email)
        if user is not None:
            request.session['number_for_reset'] = phone_number
            request.session['email'] = email
            sentOTP(phone_number)
            return redirect(otp_reset_password)
        else:
            messages.error(request, 'invalid credentials')
    else:
        return render(request, 'user/forgot_password.html')


def otp_reset_password(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        phone_number = request.session['number_for_reset']
        if checkOTP(phone_number, otp):
            return redirect(reset_password)
        else:
            messages.error(request, 'invalid otp')
    return render(request, 'user/otp_reset_password.html')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone_number = request.session['number_for_reset']
        email = request.session['email']
        if password == confirm_password:
            user = Account.objects.get(email=email, phone_number=phone_number)
            user.set_password(password)
            user.save()
        else:
            return redirect(reset_password)

        return redirect(user_login)
    else:
        return render(request, 'user/reset_password.html')
