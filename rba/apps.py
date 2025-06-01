# rba/apps.py
from django.apps import AppConfig


class RbaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rba"

    def ready(self):
        from django.contrib.auth.models import Group
        from django.db.models import TextField

        # Add the description field only if it doesn't already exist
        if not hasattr(Group, "description"):
            Group.add_to_class("description", TextField(null=True, blank=True))
