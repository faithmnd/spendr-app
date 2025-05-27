from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

def validate_image_size(image):
    max_size_mb = 2
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image size should not exceed {max_size_mb} MB")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(
        upload_to='user_photos/',
        null=True,
        blank=True,
        validators=[validate_image_size]
    )
