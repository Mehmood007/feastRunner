from django.urls import path

from accounts import views as AccountViews

from . import views

urlpatterns = [
    path("", AccountViews.my_account),
    path("profile", views.vendor_profile, name="vendor_profile"),
    path("menu_builder", views.menu_builder, name="menu_builder"),
    path(
        "menu_builder/category/<int:pk>",
        views.fooditems_by_category,
        name="fooditems_by_category",
    ),
    # Category CRUD
    path("menu_builder/category/add", views.add_category, name="add_category"),
    path(
        "menu_builder/category/edit/<int:pk>", views.edit_category, name="edit_category"
    ),
    path(
        "menu_builder/category/delete/<int:pk>",
        views.delete_category,
        name="delete_category",
    ),
    # FoodItems CRUD
    path("menu_builder/food/add", views.add_food, name="add_food"),
    path("menu_builder/food/edit/<int:pk>", views.edit_food, name="edit_food"),
    path("menu_builder/food/delete/<int:pk>", views.delete_food, name="delete_food"),
    # Opening Hours
    path("opening_hours", views.opening_hours, name="opening_hours"),
    path("opening_hours/add", views.add_opening_hours, name="add_opening_hours"),
    path(
        "opening_hours/delete/<int:pk>",
        views.delete_opening_hours,
        name="delete_opening_hours",
    ),
    # Orders from vendor prospective
    path("my_orders", views.vendor_my_orders, name="vendor_my_orders"),
    path(
        "vendor_order_details/<int:order_number>",
        views.vendor_order_details,
        name="vendor_order_details",
    ),
]
