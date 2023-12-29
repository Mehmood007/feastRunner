from django.db.models import Sum
from django.http import HttpRequest

from menu.models import FoodItem

from .models import Cart


def get_cart_counter(request: HttpRequest) -> dict:
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_count = (
                Cart.objects.filter(user=request.user).aggregate(
                    total_quantity=Sum("quantity")
                )["total_quantity"]
                or 0
            )
        except:
            pass
    return dict(cart_count=cart_count)


def get_cart_amount(request: HttpRequest) -> dict:
    sub_total = 0
    tax = 0
    grand_total = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            for item in cart_items:
                food_item = FoodItem.objects.get(pk=item.food_item.id)
                sub_total += food_item.price * item.quantity
            grand_total = sub_total + tax
        except:
            pass

    return dict(sub_total=sub_total, tax=tax, grand_total=grand_total)
