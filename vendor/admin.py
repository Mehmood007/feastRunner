from django.contrib import admin

from .models import OpeningHours, Vendor


class VendorAdmin(admin.ModelAdmin):
    list_display = ("user", "vendor_name", "is_approved", "created_at", "updated_at")
    list_display_links = ("user", "vendor_name")


class OpenHourAdmin(admin.ModelAdmin):
    list_display = ("vendor", "day", "from_hour", "to_hour")


admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHours, OpenHourAdmin)
