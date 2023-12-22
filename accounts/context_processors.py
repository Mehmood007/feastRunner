from django.conf import settings
from django.http import HttpRequest

from vendor.models import Vendor


# Return vendor
def get_vendor(request: HttpRequest) -> dict:
    if request.user.is_authenticated and request.user.role == 1:
        vendor = Vendor.objects.get(user=request.user)
        context = {"vendor": vendor}
        return context
    return dict()


# Returns api key defined in settings.py
def get_google_api_key(request: HttpRequest) -> dict:
    return {"GOOGLE_API_KEY": settings.GOOGLE_API_KEY}
