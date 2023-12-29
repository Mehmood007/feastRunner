from django.db.models import Sum
from django.http import HttpRequest

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
