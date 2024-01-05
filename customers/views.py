import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import User, UserProfile
from orders.models import Order, OrderedFood

logger = logging.getLogger("custom_logger")


# Check if user is customer
def check_role_customer(user: User) -> True or Exception:
    if user.role == 2:
        return True
    raise PermissionDenied


# "accounts/customer/profile"
@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_profile(request: HttpRequest) -> render:
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile Updated")
        else:
            messages.error(request, "Profile update failed")
            if profile_form.errors:
                logger.error(profile_form.errors)
            if user_form.errors:
                logger.error(user_form.errors)

    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    context = {
        "profile": profile,
        "profile_form": profile_form,
        "user_form": user_form,
    }
    return render(request, "customers/customer_profile.html", context)


# "accounts/customer/my_orders"
@login_required(login_url="login")
@user_passes_test(check_role_customer)
def my_orders(request: HttpRequest) -> render:
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )
    context = {
        "orders": orders,
    }
    return render(request, "customers/my_orders.html", context)


# "accounts/customer/order_details/<order_number>"
@login_required(login_url="login")
def order_details(request: HttpRequest, order_number: int) -> render or redirect:
    try:
        order = Order.objects.get(
            user=request.user, order_number=order_number, is_ordered=True
        )
        ordered_foods = OrderedFood.objects.filter(order=order)
        sub_total = 0
        for item in ordered_foods:
            sub_total += item.price * item.quantity
        tax_data = json.loads(order.tax_data)
        context = {
            "order": order,
            "ordered_foods": ordered_foods,
            "sub_total": sub_total,
            "tax_data": tax_data,
        }
    except Exception as e:
        logger.error(e)
        return redirect("home")
    return render(request, "customers/order_details.html", context)
