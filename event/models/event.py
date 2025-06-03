from django.db import models

from base_model.model import BaseModel
from users.models import CustomUser


class Calendar(BaseModel):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="calendars"
    )
    color = models.CharField(max_length=10, null=True)
    description = models.CharField(max_length=1000, blank=True)

    class Meta:
        unique_together = ("name", "user")


class Event(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    calendar = models.ForeignKey(
        Calendar, on_delete=models.CASCADE, related_name="events"
    )
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


class RecurrenceRule(BaseModel):
    FREQ_CHOICES = [
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("YEARLY", "Yearly"),
    ]

    event = models.OneToOneField(
        Event, on_delete=models.CASCADE, related_name="recurrence_rule"
    )
    frequency = models.CharField(max_length=10, choices=FREQ_CHOICES)
    interval = models.PositiveIntegerField(default=1)  # every n-th frequency
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # option


class RecurrenceWeekday(BaseModel):
    WEEKDAYS = [
        ("MO", "Monday"),
        ("TU", "Tuesday"),
        ("WE", "Wednesday"),
        ("TH", "Thursday"),
        ("FR", "Friday"),
        ("SA", "Saturday"),
        ("SU", "Sunday"),
    ]

    rule = models.ForeignKey(
        RecurrenceRule, on_delete=models.CASCADE, related_name="weekdays"
    )
    weekday = models.CharField(max_length=2, choices=WEEKDAYS)

    class Meta:
        unique_together = ("rule", "weekday")


class RecurrenceMonthDay(BaseModel):
    rule = models.ForeignKey(
        RecurrenceRule, on_delete=models.CASCADE, related_name="month_days"
    )
    day = models.IntegerField()  # 1–31

    class Meta:
        unique_together = ("rule", "day")


class RecurrenceRelativeDay(BaseModel):
    WEEKDAYS = RecurrenceWeekday.WEEKDAYS
    ORDINAL_CHOICES = [(-1, "Last"), (1, "1st"), (2, "2nd"), (3, "3rd"), (4, "4th")]

    rule = models.ForeignKey(
        RecurrenceRule, on_delete=models.CASCADE, related_name="relative_days"
    )
    weekday = models.CharField(max_length=2, choices=WEEKDAYS)
    ordinal = models.IntegerField(choices=ORDINAL_CHOICES)

    class Meta:
        unique_together = ("rule", "weekday", "ordinal")
