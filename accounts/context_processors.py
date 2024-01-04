from django.conf import settings
from django.http import HttpRequest

from accounts.models import UserProfile
from vendor.models import Vendor


# Return vendor
def get_vendor(request: HttpRequest) -> dict:
    if request.user.is_authenticated and request.user.role == 1:
        vendor = Vendor.objects.get(user=request.user)
        context = {"vendor": vendor}
        return context
    return dict()


# Return vendor
def get_customer(request: HttpRequest) -> dict:
    if request.user.is_authenticated and request.user.role == 2:
        customer = UserProfile.objects.get(user=request.user)
        context = {"customer": customer}
        return context
    return dict()


# Returns api key defined in settings.py
def get_google_api_key(request: HttpRequest) -> dict:
    return {"GOOGLE_API_KEY": settings.GOOGLE_API_KEY}


# Returns PayPal client id defined in settings.py
def get_paypal_client_id(request: HttpRequest) -> dict:
    return {"PAYPAL_CLIENT_ID": settings.PAYPAL_CLIENT_ID}
