from django.http import HttpRequest

from vendor.models import Vendor


# Return vendor
def get_vendor(request: HttpRequest) -> dict:
    if request.user.is_authenticated and request.user.role == 1:
        vendor = Vendor.objects.get(user=request.user)
        context = {"vendor": vendor}
        return context
    return dict()
