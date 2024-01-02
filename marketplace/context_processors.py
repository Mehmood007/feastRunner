from django.db.models import Sum
from django.http import HttpRequest

from menu.models import FoodItem

from .models import Cart, Tax


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
    total_tax = 0
    grand_total = 0
    tax_dict = dict()
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            food_item = FoodItem.objects.get(pk=item.food_item.id)
            sub_total += food_item.price * item.quantity
        applicable_taxes = Tax.objects.filter(is_active=True)
        for tax in applicable_taxes:
            tax_type = str(tax.tax_type)
            tax_percentage = tax.tax_percentage
            tax_amount = round((tax_percentage * sub_total) / 100, 2)
            total_tax += tax_amount
            tax_dict[tax_type] = {str(tax_percentage): str(tax_amount)}
        grand_total = sub_total + total_tax

    return dict(
        sub_total=sub_total, tax=total_tax, grand_total=grand_total, tax_dict=tax_dict
    )
