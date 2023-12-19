from .models import User


def detect_user(user: User) -> str:
    if user.role == 1:
        return "vendor_dashboard"
    if user.role == 2:
        return "customer_dashboard"
    if user.role == None and user.is_superadmin:
        return "/admin"
