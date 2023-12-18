import logging

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render

from .forms import UserForm
from .models import User

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
