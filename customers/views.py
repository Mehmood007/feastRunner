import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import User, UserProfile

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
