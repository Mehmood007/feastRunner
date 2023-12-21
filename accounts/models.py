import os

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str = None,
    ):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have an username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str = None,
    ):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = {
        (VENDOR, "Vendor"),
        (CUSTOMER, "Customer"),
    }
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=14, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    # Required fields
    date_joined = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm: str, obj=None) -> bool:
        return self.is_admin

    def has_module_perms(self, app_label: str) -> bool:
        return True

    def get_role(self) -> str:
        if self.role == 1:
            return "Vendor"
        if self.role == 2:
            return "Customer"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="users/profile_pictures", blank=True, null=True
    )
    cover_photo = models.ImageField(
        upload_to="users/cover_photos", blank=True, null=True
    )
    address_line_1 = models.CharField(max_length=50, blank=True, null=True)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_address(self) -> str:
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self) -> str:
        return self.user.email

    def delete(self, *args, **kwargs) -> None:
        # Delete the file associated with the model instance
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        if self.cover_photo:
            if os.path.isfile(self.cover_photo.path):
                os.remove(self.cover_photo.path)
        super(UserProfile, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs) -> models.Model:
        if self.pk:
            # if updated delete previous pictures
            original_obj = UserProfile.objects.get(pk=self.pk)
            if original_obj.profile_picture != self.profile_picture:
                if os.path.isfile(original_obj.profile_picture.path):
                    os.remove(original_obj.profile_picture.path)
            if original_obj.cover_photo != self.cover_photo:
                if os.path.isfile(original_obj.cover_photo.path):
                    os.remove(original_obj.cover_photo.path)
        return super(UserProfile, self).save(*args, **kwargs)
