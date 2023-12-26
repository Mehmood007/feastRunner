import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import User, UserProfile
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem

from .forms import VendorForm
from .models import Vendor

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
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(form.cleaned_data["category_name"])
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
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(form.cleaned_data["category_name"])
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
