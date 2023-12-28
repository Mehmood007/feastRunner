from django.db.models import Prefetch
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from menu.models import Category, FoodItem
from vendor.models import Vendor


# "marketplace/"
def marketplace(request: HttpRequest) -> render:
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendors_count = len(vendors)
    context = {
        "vendors_count": vendors_count,
        "vendors": vendors,
    }
    return render(request, "marketplace/listings.html", context)


# "marketplace/<vendor-slug>"
def vendor_details(request: HttpRequest, vendor_slug: str) -> render:
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(
        vendor=vendor, vendor__is_approved=True
    ).prefetch_related(
        Prefetch("food_items", queryset=FoodItem.objects.filter(is_available=True))
    )
    context = {
        "categories": categories,
        "vendor": vendor,
    }
    return render(request, "marketplace/vendor_details.html", context)
