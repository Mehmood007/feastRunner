from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor

from .context_processors import get_cart_amount, get_cart_counter


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
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        "cart_items": cart_items,
        "categories": categories,
        "vendor": vendor,
    }
    return render(request, "marketplace/vendor_details.html", context)


# "marketplace/add_to_cart/<food_id>"
def add_to_cart(request: HttpRequest, food_id: int) -> JsonResponse:
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                food_item = FoodItem.objects.get(id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, food_item=food_item)
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Increased cart quantity",
                            "cart_count": get_cart_counter(request)["cart_count"],
                            "qty": chkCart.quantity,
                            "cart_amount": get_cart_amount(request),
                        }
                    )
                except:
                    Cart.objects.create(
                        user=request.user, food_item=food_item, quantity=1
                    )
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Item added successfully",
                            "cart_count": get_cart_counter(request)["cart_count"],
                            "qty": 1,
                            "cart_amount": get_cart_amount(request),
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "failed", "message": "No such item exists"}
                )
        else:
            return JsonResponse({"status": "failed", "message": "Request must be ajax"})

    return JsonResponse(
        {"status": "login_required", "message": "Please login to continue"}
    )


# "marketplace/decrease_cart/<food_id>"
def decrease_cart(request: HttpRequest, food_id: int) -> JsonResponse:
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            try:
                food_item = FoodItem.objects.get(id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, food_item=food_item)
                    chkCart.quantity -= 1
                    if chkCart.quantity <= 0:
                        chkCart.delete()
                    else:
                        chkCart.save()
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": "Increased cart quantity",
                            "cart_count": get_cart_counter(request)["cart_count"],
                            "qty": chkCart.quantity,
                            "cart_amount": get_cart_amount(request),
                        }
                    )
                except:
                    return JsonResponse(
                        {
                            "status": "failed",
                            "message": "No such items in cart",
                            "cart_count": get_cart_counter(request)["cart_count"],
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "failed", "message": "No such item exists"}
                )
        else:
            return JsonResponse({"status": "failed", "message": "Request must be ajax"})

    return JsonResponse(
        {"status": "login_required", "message": "Please login to continue"}
    )


# "marketplace/cart"
@login_required(login_url="login")
def cart(request: HttpRequest) -> render:
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    context = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", context)


# "marketplace/delete_cart/<int: food_id>"
@login_required(login_url="login")
def delete_cart(request: HttpRequest, food_id: int) -> render:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            food_item = FoodItem.objects.get(id=food_id)
            try:
                chkCart = Cart.objects.get(user=request.user, food_item=food_item)
                chkCart.delete()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Item deleted successfully",
                        "cart_count": get_cart_counter(request)["cart_count"],
                        "cart_amount": get_cart_amount(request),
                    }
                )
            except:
                return JsonResponse(
                    {
                        "status": "failed",
                        "message": "No such items in cart",
                        "cart_count": get_cart_counter(request)["cart_count"],
                    }
                )
        except:
            return JsonResponse({"status": "failed", "message": "No such item exists"})
    else:
        return JsonResponse({"status": "failed", "message": "Request must be ajax"})
