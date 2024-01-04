from django.contrib import admin

from .models import Order, OrderedFood, Payment


class OrderedFoodItemInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ["order", "payment", "user", "fooditem"]
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "name",
        "phone_number",
        "email",
        "total",
        "payment_method",
        "status",
        "is_ordered",
    ]
    inlines = [OrderedFoodItemInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
admin.site.register(Payment)
