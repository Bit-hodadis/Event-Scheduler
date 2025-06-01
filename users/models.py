from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from base_model.model import BaseModel

from .managers import CustomUserManager


class CustomUser(AbstractUser, BaseModel):
    objects = CustomUserManager()
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default="F", help_text="Gender."
    )
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, help_text="Optional phone number."
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        help_text="Profile picture.",
    )
    date_of_birth = models.DateField(blank=True, null=True, help_text="Date of birth.")
    is_verified = models.BooleanField(
        default=False, help_text="Email verification status."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"  # Set email as the login field
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]  # Required fields for superuser creation

    @property
    def latest_status(self):
        """Get the latest status of the user."""
        latest_status = self.status_history.order_by("-timestamp").first()
        return latest_status.status if latest_status else "ACTIVE"


class UserHasStatus(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DEACTIVATED", "Deactivated"),
    ]
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="status_history"
    )
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_changes",
        help_text="The admin or user who changed the status.",
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    reason = models.TextField(
        blank=True, null=True, help_text="Reason for status change."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} -> {self.status} by {self.changed_by.username if self.changed_by else 'System'} at {self.timestamp}"
