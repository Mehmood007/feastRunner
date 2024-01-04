import logging

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode

from orders.models import Order
from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile
from .utils import detect_user, send_verification_email

logger = logging.getLogger("custom_logger")


# Check if user is vendor
def check_role_vendor(user: User) -> True or Exception:
    if user.role == 1:
        return True
    raise PermissionDenied


# Check if user is customer
def check_role_customer(user: User) -> True or Exception:
    if user.role == 2:
        return True
    raise PermissionDenied


# "accounts/registerUser"
def registerUser(request: HttpRequest) -> render or redirect:
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("my_account")
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.set_password(password)
            user.save()
            # send verification mail
            mail_subject = "Activate Account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)
            messages.success(request, "Your account has been register successfully")
            return redirect("login")
        else:
            messages.error(request, "Failed to register account")
            logger.error(form.errors)
    else:
        form = UserForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/registerUser.html", context)


# "accounts/registerVendor"
def registerVendor(request: HttpRequest) -> render or redirect:
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("my_account")
    if request.method == "POST":
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            password = form.cleaned_data["password"]
            user = form.save(commit=False)
            user.role = User.VENDOR
            user.set_password(password)
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data["vendor_name"]
            vendor.vendor_slug = slugify(f"{vendor_name}-{user.id}")
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            # send verification mail
            mail_subject = "Activate Account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)
            messages.success(
                request,
                "Your request has been submitted successfully. Please wait for the approval",
            )
            return redirect("login")
        else:
            messages.error(request, "Failed to register business")
            logger.error(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        "v_form": v_form,
        "form": form,
    }
    return render(request, "accounts/registerVendor.html", context)


# "accounts/login"
def login(request: HttpRequest) -> render or redirect:
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("my_account")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You have logged in successfully")
            return redirect("my_account")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, "accounts/login.html")


# "accounts/logout"
def logout(request: HttpRequest) -> render or redirect:
    auth.logout(request)
    messages.info(request, "Successfully logged out")
    return redirect("login")


# "accounts/my_account"
@login_required(login_url="login")
def my_account(request: HttpRequest) -> redirect:
    user = request.user
    redirect_url = detect_user(user)
    return redirect(redirect_url)


# "accounts/customerdashboard"
@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_dashboard(request: HttpRequest) -> render or redirect:
    orders_count = Order.objects.filter(user=request.user, is_ordered=True).count()
    orders = Order.objects.filter(user=request.user, is_ordered=True)[:5]
    context = {
        "orders": orders,
        "orders_count": orders_count,
    }
    return render(request, "accounts/customerdashboard.html", context)


# "accounts/vendordashboard"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request: HttpRequest) -> render or redirect:
    return render(request, "accounts/vendordashboard.html")


# "activate/<uidb64>/<token>"
def activate(request: HttpRequest, uidb64: str, token: str) -> redirect:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account is activated")
        return redirect("my_account")
    else:
        messages.error(request, "Invalid activation url")
        return redirect("home")


# "accounts/forgot-password"
def forgot_password(request: HttpRequest) -> render or redirect:
    if request.method == "POST":
        email = request.POST["email"]
        user = User.objects.filter(email=email).first() or None
        if user is not None:
            mail_subject = "Password Reset"
            mail_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, mail_template)
            messages.success(request, "Password reset link has been sent to your mail")
            return redirect("login")
        else:
            messages.error(request, "Given mail is not registered")
            return redirect("forgot_password")
    return render(request, "accounts/forgot_password.html")


# "accounts/reset-password-validate/<uidb64>/<token>"
def reset_password_validate(
    request: HttpRequest,
    uidb64: str,
    token: str,
) -> render or redirect:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "Reset Link has been expired")
        return redirect("forgot_password")


# "accounts/reset-password"
def reset_password(request: HttpRequest) -> render or redirect:
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Successfully changed password")
            return redirect("login")
        else:
            messages.error(request, "Passwords did not match")
            return redirect("reset_password")
    return render(request, "accounts/emails/reset_password.html")
