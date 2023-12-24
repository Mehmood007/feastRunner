import os

from django.core.exceptions import ValidationError

valid_image_extensions = frozenset({".jpg", ".png", ".jpeg"})


def allow_only_images_validator(file_name: str) -> Exception or None:
    ext = os.path.splitext(file_name.name)[1]
    if ext.lower() not in valid_image_extensions:
        raise ValidationError(
            f"Invalid file type. only {str(valid_image_extensions)} file types are allowed"
        )
