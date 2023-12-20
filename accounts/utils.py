from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import User


def detect_user(user: User) -> str:
    if user.role == 1:
        return "vendor_dashboard"
    if user.role == 2:
        return "customer_dashboard"
    if user.role == None and user.is_superadmin:
        return "/admin"


def send_verification_email(
    request: HttpRequest, user: User, mail_subject: str, mail_template: str
) -> None:
    current_site = get_current_site(request)
    message = render_to_string(
        mail_template,
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    to_email = user.email
    mail = EmailMessage(mail_subject, message, to=[to_email])
    mail.send()
