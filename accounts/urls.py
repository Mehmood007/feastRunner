from django.urls import path

from . import views

urlpatterns = [
    path("registerUser", views.registerUser, name="registerUser"),
    path("registerVendor", views.registerVendor, name="registerVendor"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("my_account", views.my_account, name="my_account"),
    path("customerdashboard", views.customer_dashboard, name="customer_dashboard"),
    path("vendordashboard", views.vendor_dashboard, name="vendor_dashboard"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
]
