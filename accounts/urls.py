from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.my_account),
    # User registrations
    path("registerUser", views.registerUser, name="registerUser"),
    path("registerVendor", views.registerVendor, name="registerVendor"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    # User Dashboards
    path("my-account", views.my_account, name="my_account"),
    path("customerdashboard", views.customer_dashboard, name="customer_dashboard"),
    path("vendordashboard", views.vendor_dashboard, name="vendor_dashboard"),
    # Password management
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path(
        "reset_password_validate/<uidb64>/<token>",
        views.reset_password_validate,
        name="reset_password_validate",
    ),
    path("reset_password/", views.reset_password, name="reset_password"),
    # vendor
    path("vendor/", include("vendor.urls")),
]
