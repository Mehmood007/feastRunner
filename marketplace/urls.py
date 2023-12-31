from django.urls import path

from . import views

urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    path("<slug:vendor_slug>", views.vendor_details, name="vendor_details"),
    # CART
    path("cart/", views.cart, name="cart"),
    path("add_to_cart/<int:food_id>", views.add_to_cart, name="add_to_cart"),
    path("decrease_cart/<int:food_id>", views.decrease_cart, name="decrease_cart"),
    path("delete_cart/<int:food_id>", views.delete_cart, name="delete_cart"),
    path("search/", views.search, name="search"),
    # CHECK OUT
    path("checkout/", views.checkout, name="checkout"),
]
