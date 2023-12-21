from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userprofile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=100)
    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.vendor_name

    def save(self, *args, **kwargs) -> models.Model:
        if self.pk is not None:
            original = Vendor.objects.get(pk=self.pk)
            if original.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                }
                if self.is_approved == True:
                    mail_subject = "Congratulations! Your business has been approved"
                else:
                    mail_subject = "Sorry! Your business could not approved"
                send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)
