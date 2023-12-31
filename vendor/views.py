import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import User, UserProfile
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from orders.models import Order, OrderedFood

from .forms import OpeningHoursForm, VendorForm
from .models import OpeningHours, Vendor

logger = logging.getLogger("custom_logger")


# Get current_vendor
def get_vendor(request: HttpRequest) -> Vendor:
    return Vendor.objects.get(user=request.user)


# Check if user is vendor
def check_role_vendor(user: User) -> True or Exception:
    if user.role == 1:
        return True
    raise PermissionDenied


# "accounts/vendor/profile"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_profile(request: HttpRequest) -> render:
    vendor = get_object_or_404(Vendor, user=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if user_profile_form.is_valid() and vendor_form.is_valid():
            user_profile_form.save()
            vendor_form.save()
            messages.success(request, "Successfully update restaurant")
        else:
            if user_profile_form.errors:
                logger.error(user_profile_form.errors)
            if vendor_form.errors:
                logger.error(vendor_form.errors)
            messages.error(request, "Sorry we could not change restaurant details")
    else:
        user_profile_form = UserProfileForm(instance=user_profile)
        vendor_form = VendorForm(instance=vendor)
    context = {
        "profile": user_profile,
        "user_profile_form": user_profile_form,
        "vendor_form": vendor_form,
    }
    return render(request, "vendor/vendor_profile.html", context)


# "accounts/vendor/profile/menu_builder"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menu_builder(request: HttpRequest) -> render:
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by("created_at")
    context = {
        "categories": categories,
    }
    return render(request, "vendor/menu_builder.html", context)


# "accounts/vendor/menu_builder/category/<int:pk>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def fooditems_by_category(request: HttpRequest, pk: int = None) -> render:
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    food_items = FoodItem.objects.filter(category=category, vendor=vendor)
    context = {
        "category": category,
        "food_items": food_items,
    }
    return render(request, "vendor/fooditems_by_category.html", context)


# "accounts/vendor/menu_builder/category/add"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_category(request: HttpRequest) -> render or redirect:
    if request.method == "POST":
        form = CategoryForm(request.POST.copy())
        form.data["vendor"] = get_vendor(request)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = slugify(form.cleaned_data["category_name"])
            category.save()
            category.slug = (
                f"{slugify(form.cleaned_data['category_name'])}-{category.id}"
            )
            category.save()
            messages.success(request, "Category added successfully")
            return redirect("menu_builder")
        else:
            messages.error(request, "Sorry Category can not be added")
            logger.error(form.errors)
    else:
        form = CategoryForm()
    context = {
        "form": form,
    }
    return render(request, "vendor/add_category.html", context)


# "accounts/vendor/menu_builder/category/edit/<int:pk>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_category(request: HttpRequest, pk: int) -> render or redirect:
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST.copy(), instance=category)
        form.data["vendor"] = get_vendor(request)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = (
                f"{slugify(form.cleaned_data['category_name'])}-{category.id}"
            )
            category.save()
            messages.success(request, "Category added successfully")
            return redirect("menu_builder")
        else:
            messages.error(request, "Sorry Category can not be added")
            logger.error(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        "form": form,
        "category": category,
    }
    return render(request, "vendor/edit_category.html", context)


# "accounts/vendor/menu_builder/category/edit/<int:pk>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_category(request: HttpRequest, pk: int) -> redirect:
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully...")
    return redirect("menu_builder")


# "accounts/vendor/menu_builder/food/add"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_food(request: HttpRequest) -> render or redirect:
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            fooditem = form.save(commit=False)
            food_title = form.cleaned_data["food_title"]
            fooditem.vendor = get_vendor(request)
            fooditem.save()
            fooditem.slug = f"{slugify(food_title)}-{fooditem.id}"
            fooditem.save()
            messages.success(request, "Successfully added food item")
            return redirect("fooditems_by_category", fooditem.category.id)
        else:
            messages.error(request, "Sorry could not save this food item")
            logger.error(form.errors)
    else:
        form = FoodItemForm()
        form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
    context = {
        "form": form,
    }
    return render(request, "vendor/add_food.html", context)


# "accounts/vendor/menu_builder/food/edit/<int:pk>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_food(request: HttpRequest, pk: int) -> render or redirect:
    fooditem = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=fooditem)
        if form.is_valid():
            fooditem = form.save(commit=False)
            food_title = form.cleaned_data["food_title"]
            fooditem.vendor = get_vendor(request)
            fooditem.slug = f"{slugify(food_title)}-{fooditem.id}"
            fooditem.save()
            messages.success(request, "Food item added successfully")
            return redirect("fooditems_by_category", fooditem.category.id)
        else:
            messages.error(request, "Sorry could not save this food item")
            logger.error(form.errors)
    else:
        form = FoodItemForm(instance=fooditem)
        form.fields["category"].queryset = Category.objects.filter(
            vendor=get_vendor(request)
        )
    context = {
        "form": form,
        "fooditem": fooditem,
    }
    return render(request, "vendor/edit_food.html", context)


# "accounts/vendor/menu_builder/food/delete/<int:pk>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_food(request: HttpRequest, pk: int) -> render or redirect:
    fooditem = get_object_or_404(FoodItem, pk=pk)
    fooditem.delete()
    messages.success(request, "Fooditem deleted successfully...")
    return redirect("fooditems_by_category", fooditem.category.id)


# "accounts/vendor/opening_hours"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def opening_hours(request: HttpRequest) -> render:
    opening_hours = OpeningHours.objects.filter(vendor=get_vendor(request))
    form = OpeningHoursForm()
    context = {
        "opening_hours": opening_hours,
        "form": form,
    }
    return render(request, "vendor/opening_hours.html", context)


# "accounts/vendor/opening_hours/add"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_opening_hours(request: HttpRequest) -> JsonResponse:
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        day = request.POST.get("day")
        from_hour = request.POST.get("from_hour")
        to_hour = request.POST.get("to_hour")
        is_closed = request.POST.get("is_closed")
        try:
            hour = OpeningHours.objects.create(
                vendor=get_vendor(request),
                day=day,
                from_hour=from_hour,
                to_hour=to_hour,
                is_closed=is_closed,
            )
            if hour:
                day = OpeningHours.objects.get(id=hour.id)
                if day.is_closed:
                    response = {
                        "id": day.id,
                        "day": day.get_day_display(),
                        "is_closed": day.is_closed,
                    }
                else:
                    response = {
                        "id": day.id,
                        "day": day.get_day_display(),
                        "is_closed": day.is_closed,
                        "from_hour": day.from_hour,
                        "to_hour": day.to_hour,
                    }
                response["status"] = "success"
                response["message"] = "Form added successfully"
        except Exception as e:
            logger.error(e)
            response = {"status": "failed", "message": "Sorry form could not be added"}
            if isinstance(e, IntegrityError):
                response["message"] = "Same record already exists"
        finally:
            return JsonResponse(response)
    return JsonResponse({"status": "bad request"})


# "accounts/vendor/opening_hours/delete/<int:pk>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_opening_hours(request: HttpRequest, pk: int) -> JsonResponse:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        hours = get_object_or_404(OpeningHours, pk=pk)
        hours.delete()
        return JsonResponse({"status": "success", "id": pk})
    return JsonResponse({"status": "failed", "id": pk})


# "accounts/vendor/order_details/<order_number>"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_order_details(request: HttpRequest, order_number: int) -> JsonResponse:
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_foods = OrderedFood.objects.filter(
            order=order, fooditem__vendor=get_vendor(request)
        )
        context = {
            "order": order,
            "ordered_foods": ordered_foods,
            "sub_total": order.get_total_by_vendor["sub_total"],
            "tax_data": order.get_total_by_vendor["tax_dict"],
            "total": order.get_total_by_vendor["grand_total"],
        }
    except Exception as e:
        logger.error(e)
        return redirect("home")
    return render(request, "vendor/vendor_order_details.html", context)


# "accounts/vendor/my_orders"
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_my_orders(request: HttpRequest) -> render:
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by(
        "-created_at"
    )
    context = {
        "orders": orders,
    }
    return render(request, "vendor/my_orders.html", context)
