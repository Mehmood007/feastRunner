import logging

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render

from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile

logger = logging.getLogger("custom_logger")


# "accounts/registerUser"
def registerUser(request: HttpRequest) -> render or redirect:
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.set_password(password)
            user.save()
            messages.success(request, "Your account has been register successfully")
            return redirect("home")
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
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            messages.success(
                request,
                "Your request has been submitted successfully. Please wait for the approval",
            )
            return redirect("home")
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
