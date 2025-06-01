# audit/models.py
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from base_model.model import BaseModel


class AuditLog(BaseModel):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        # ("LOGIN", "Login"),
        # ("LOGOUT", "Logout"),
        # ("VIEW", "View"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource = models.CharField(max_length=255)  # Table name, API endpoint, etc.

    object_id = models.TextField()  # Store the primary key of the related object

    previous_snapshot = models.JSONField(
        null=True, blank=True
    )  # Previous state snapshot
    updated_snapshot = models.JSONField(null=True, blank=True)  # Updated state snapshot
    table_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} performed {self.action} on {self.resource}"


class LoginLog(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=[("SUCCESS", "Success"), ("FAILURE", "Failure")]
    )

    os = models.CharField(max_length=1000, null=True)
    browser = models.CharField(max_length=1000, null=True)
    device_name = models.TextField(null=True)
    is_revoked = models.BooleanField(default=False)
    is_remember = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} login {self.status} at {self.login_time}"
