import os
from datetime import date, datetime, time

from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userprofile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=100)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_open(self):
        today = date.today().isoweekday()
        current_opening_hours = OpeningHours.objects.filter(vendor=self, day=today)
        current_time = datetime.now().strftime("%H:%M:%S")
        is_open = False
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                if current_time >= start and current_time <= end:
                    is_open = True
                    break
        return is_open

    def __str__(self) -> str:
        return self.vendor_name

    def save(self, *args, **kwargs) -> models.Model:
        if self.pk is not None:
            original = Vendor.objects.get(pk=self.pk)
            if original.vendor_license != self.vendor_license:
                if os.path.isfile(original.vendor_license.path):
                    os.remove(original.vendor_license.path)
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


DAYS = [
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]

HOUR_OF_DAY_24 = [
    (time(h, m).strftime("%I:%M %p"), time(h, m).strftime("%I:%M %p"))
    for h in range(0, 24)
    for m in (0, 30)
]


class OpeningHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ("day", "-from_hour")
        unique_together = ("vendor", "day", "from_hour", "to_hour")

    def __str__(self) -> str:
        return self.get_day_display()
