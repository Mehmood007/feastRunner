from typing import Any

from django import forms

from .models import User, UserProfile
from .validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean(self) -> dict[str, Any]:
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords does not match")
        return super().clean()


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )
    cover_photo = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
            "cover_photo",
            "address",
            "country",
            "state",
            "city",
            "pin_code",
            "longitude",
            "latitude",
        ]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields["longitude"].widget.attrs["readonly"] = "readonly"
        self.fields["latitude"].widget.attrs["readonly"] = "readonly"


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number"]
