import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from address.models import Address
from plan.models.planning_request import PlanningRequest
from users.models import CustomUser


class Command(BaseCommand):
    help = "creating Role"

    def handle(self, *args, **options):
        # Prompt for first_name and last_name if not provided
        PlanningRequest.objects.all().delete()
        # data = CustomUser.objects.all().first()

        # address = Address.objects.create(name="Oromia", created_by=data, parent=None)
