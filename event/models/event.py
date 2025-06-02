from django.db import models

from base_model.model import BaseModel
from users.models import CustomUser


class Event(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    is_recurring = models.BooleanField(default=False)
    timezone = models.CharField(
        max_length=64,
        default="UTC",
        help_text="Timezone name, e.g., 'Africa/Addis_Ababa'",
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["user", "start_time"]),
            models.Index(fields=["is_recurring"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_time})"
