import os

from django.db import models
from django.forms import ValidationError

from vendor.models import Vendor


class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.category_name

    def clean(self) -> None:
        self.category_name = self.category_name.capitalize()
        existing_category = Category.objects.filter(
            vendor=self.vendor, category_name=self.category_name
        )
        if self.pk:
            existing_category = existing_category.exclude(pk=self.pk)
        if existing_category.exists():
            raise ValidationError("Category name must be unique for each vendor.")
        return super().clean()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        unique_together = ("vendor", "category_name")


class FoodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    food_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="food_images")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.food_title

    def delete(self, *args, **kwargs) -> None:
        # Delete the file associated with the model instance
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super(FoodItem, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs) -> models.Model:
        if self.pk:
            # if updated delete previous pictures
            original_obj = FoodItem.objects.get(pk=self.pk)
            if original_obj.image != self.image:
                if os.path.isfile(original_obj.image.path):
                    os.remove(original_obj.image.path)
        return super(FoodItem, self).save(*args, **kwargs)
