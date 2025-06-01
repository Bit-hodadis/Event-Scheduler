import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from localization.models import Entity, EntityTranslation, Language
from users.models import CustomUser


class Command(BaseCommand):
    help = "creating Role"

    def handle(self, *args, **options):
        # Prompt for first_name and last_name if not provided

        data = CustomUser.objects.get(name="en").delete()

        languages = [
            # {"locale": "en", "name": "English"},
            {"locale": "am", "name": "Amharic"},
            {"locale": "oro", "name": "Oromigna"},
        ]

        for language in languages:
            Language.objects.get_or_create(
                locale=language["locale"], name=language["name"]
            )
