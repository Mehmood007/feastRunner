from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render

from .models import Vendor


# Check if user is vendor
def check_role_vendor(user) -> bool or Exception:
    if user.role == 1:
        return True
    raise PermissionDenied


# "accounts/vendor/profile"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_profile(request: HttpRequest) -> render:
    return render(request, "vendor/vendor_profile.html")
