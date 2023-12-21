import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserProfileForm
from accounts.models import UserProfile

from .forms import VendorForm
from .models import Vendor

logger = logging.getLogger("custom_logger")


# Check if user is vendor
def check_role_vendor(user) -> bool or Exception:
    if user.role == 1:
        return True
    raise PermissionDenied


# "accounts/vendor/profile"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_profile(request: HttpRequest) -> render or redirect:
    vendor = get_object_or_404(Vendor, user=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if user_profile_form.is_valid() and vendor_form.is_valid():
            user_profile_form.save()
            vendor_form.save()
            messages.success(request, "Successfully update restaurant")
        else:
            if user_profile_form.errors:
                logger.error(user_profile_form.errors)
            if vendor_form.errors:
                logger.error(vendor_form.errors)
            messages.error(request, "Sorry we could not change restaurant details")
    else:
        user_profile_form = UserProfileForm(instance=user_profile)
        vendor_form = VendorForm(instance=vendor)
    context = {
        "profile": user_profile,
        "user_profile_form": user_profile_form,
        "vendor_form": vendor_form,
    }
    return render(request, "vendor/vendor_profile.html", context)
