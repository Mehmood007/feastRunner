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
]
