# serializers.py

from rest_framework import serializers

from event.models.event import (
    Calendar,
    Event,
    RecurrenceMonthDay,
    RecurrenceRelativeDay,
    RecurrenceRule,
    RecurrenceWeekday,
)


class RecurrenceWeekdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceWeekday
        fields = ["id", "weekday"]


class RecurrenceMonthDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceMonthDay
        fields = ["id", "day"]


class RecurrenceRelativeDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceRelativeDay
        fields = ["id", "weekday", "ordinal"]


class RecurrenceRuleSerializer(serializers.ModelSerializer):
    weekdays = RecurrenceWeekdaySerializer(many=True, required=False)
    month_days = RecurrenceMonthDaySerializer(many=True, required=False)
    relative_days = RecurrenceRelativeDaySerializer(many=True, required=False)

    class Meta:
        model = RecurrenceRule
        fields = [
            "id",
            "frequency",
            "interval",
            "start_date",
            "end_date",
            "weekdays",
            "month_days",
            "relative_days",
        ]

    def create(self, validated_data):
        weekdays_data = validated_data.pop("weekdays", [])
        month_days_data = validated_data.pop("month_days", [])
        relative_days_data = validated_data.pop("relative_days", [])

        rule = RecurrenceRule.objects.create(**validated_data)

        for day in weekdays_data:
            RecurrenceWeekday.objects.create(rule=rule, **day)
        for day in month_days_data:
            RecurrenceMonthDay.objects.create(rule=rule, **day)
        for day in relative_days_data:
            RecurrenceRelativeDay.objects.create(rule=rule, **day)

        return rule

    def update(self, instance, validated_data):
        weekdays_data = validated_data.pop("weekdays", [])
        month_days_data = validated_data.pop("month_days", [])
        relative_days_data = validated_data.pop("relative_days", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear existing related data
        instance.weekdays.all().delete()
        instance.month_days.all().delete()
        instance.relative_days.all().delete()

        # Re-create
        for day in weekdays_data:
            RecurrenceWeekday.objects.create(rule=instance, **day)
        for day in month_days_data:
            RecurrenceMonthDay.objects.create(rule=instance, **day)
        for day in relative_days_data:
            RecurrenceRelativeDay.objects.create(rule=instance, **day)

        return instance


class EventSerializer(serializers.ModelSerializer):
    recurrence_rule = RecurrenceRuleSerializer(required=False)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "calendar",
            "start_time",
            "end_time",
            "timezone",
            "is_recurring",
            "recurrence_rule",
        ]

    def create(self, validated_data):
        recurrence_data = validated_data.pop("recurrence_rule", None)
        event = Event.objects.create(**validated_data)
        if event.is_recurring and recurrence_data:
            recurrence_data["event"] = event
            RecurrenceRuleSerializer().create(recurrence_data)
        return event

    def update(self, instance, validated_data):
        recurrence_data = validated_data.pop("recurrence_rule", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if recurrence_data:
            if hasattr(instance, "recurrence_rule"):
                RecurrenceRuleSerializer().update(
                    instance.recurrence_rule, recurrence_data
                )
            else:
                recurrence_data["event"] = instance
                RecurrenceRuleSerializer().create(recurrence_data)

        return instance


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ["id", "name", "color", "description"]
