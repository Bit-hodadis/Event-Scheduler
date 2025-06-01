from getpass import getpass

from django.contrib.auth.management.commands.createsuperuser import (
    Command as BaseCommand,
)
from django.core.management import CommandError


class Command(BaseCommand):
    help = "Create a superuser with mandatory first_name and last_name."

    def handle(self, *args, **options):
        # Prompt for first_name and last_name if not provided
        if not options.get("first_name"):
            options["first_name"] = input("First name: ").strip()
            if not options["first_name"]:
                raise CommandError("The first name cannot be blank.")

        if not options.get("last_name"):
            options["last_name"] = input("Last name: ").strip()
            if not options["last_name"]:
                raise CommandError("The last name cannot be blank.")

        super().handle(*args, **options)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--first_name", type=str, help="First name of the superuser"
        )
        parser.add_argument("--last_name", type=str, help="Last name of the superuser")
