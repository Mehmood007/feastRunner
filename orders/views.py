import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render

from accounts.utils import send_notification
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart, Tax
from menu.models import FoodItem

from .forms import OrderForm
from .models import Order, OrderedFood, Payment
from .utils import generate_order_number

logger = logging.getLogger("custom_logger")


# "orders/place_order"
@login_required(login_url="login")
def place_order(request: HttpRequest) -> render:
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    get_tax = Tax.objects.filter(is_active=True)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("marketplace")
    vendors_ids = {item.food_item.vendor.id for item in cart_items}
    sub_total = 0
    k = {}
    total_data = {}
    for item in cart_items:
        food_item = FoodItem.objects.get(
            pk=item.food_item.id, vendor_id__in=vendors_ids
        )
        vendor_id = food_item.vendor.id
        if vendor_id in k:
            sub_total = k[vendor_id]
            sub_total += food_item.price * item.quantity
            k[vendor_id] = sub_total
        else:
            sub_total = food_item.price * item.quantity
            k[vendor_id] = sub_total
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * sub_total) / 100, 2)
            tax_dict[tax_type] = {str(tax_percentage): str(tax_amount)}
        total_data[food_item.vendor.id] = {str(sub_total): str(tax_dict)}

    cart_amount = get_cart_amount(request)
    sub_total = cart_amount["sub_total"]
    total_tax = cart_amount["tax"]
    grand_total = cart_amount["grand_total"]
    tax_data = cart_amount["tax_dict"]
    if request.POST:
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.total_data = json.dumps(total_data)
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            context = {"order": order, "cart_items": cart_items}
            return render(request, "orders/place_order.html", context)
        else:
            messages.error(request, "Failed to register account")
            logger.error(order_form.errors)
    return render(request, "orders/place_order.html")


# "orders/payments"
@login_required(login_url="login")
def payments(request: HttpRequest) -> JsonResponse:
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        vendor_emails = set()
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            vendor_emails.add(item.food_item.vendor.user.email)
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.food_item
            ordered_food.quantity = item.quantity
            ordered_food.price = item.food_item.price
            ordered_food.amount = item.food_item.price * item.quantity
            ordered_food.save()

        mail_subject = "Thank you for ordering"
        email_template = "orders/order_confirmation_email.html"
        context = {
            "user": request.user,
            "order": order,
            "to_email": order.email,
        }
        send_notification(mail_subject, email_template, context)
        mail_subject = "You have received new order"
        email_template = "orders/new_order_received.html"
        context = {
            "user": request.user,
            "order": order,
            "to_email": vendor_emails,
        }
        send_notification(mail_subject, email_template, context)
        cart_items.delete()
        response = {
            status: "success",
            "order_number": order_number,
            "transaction_id": transaction_id,
        }
        return JsonResponse(response)

    return JsonResponse({"status": "failure"})


# "orders/order_complete"
@login_required(login_url="login")
def order_complete(request: HttpRequest) -> render or redirect:
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")
    try:
        order = Order.objects.get(
            order_number=order_number, payment__transaction_id=transaction_id
        )
        ordered_foods = OrderedFood.objects.filter(order=order)
        sub_total = 0
        for item in ordered_foods:
            sub_total += item.price * item.quantity

        tax_data = json.loads(order.tax_data)
        context = {
            "order": order,
            "ordered_foods": ordered_foods,
            "sub_total": sub_total,
            "tax_data": tax_data,
        }
    except:
        return redirect("home")
    return render(request, "orders/order_complete.html", context)
