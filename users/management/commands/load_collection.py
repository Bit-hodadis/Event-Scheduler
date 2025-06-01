from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from tax.models.tax_center import TaxCenter
from tax.models.tax_collection import TaxCollection
from tax.models.tax_plan import TaxPlan
from tax.models.tax_type import TaxType
from users.models import CustomUser


class Command(BaseCommand):
    help = "Populate dummy data for Tax Plans and Tax Collections"

    def handle(self, *args, **kwargs):
        # Create necessary foreign keys
        tax_center = TaxCenter.objects.all().first()

        tax_type = TaxType.objects.all().first()
        user = CustomUser.objects.all().first()

        # Create Tax Plan
        tax_plan, created = TaxPlan.objects.get_or_create(
            name="Sample Tax Plan",
            year="2025",
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date(),
            created_by=user,
            tax_center=tax_center,
            tax_type=tax_type,
            defaults={"rate": 15},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Tax Plan: {tax_plan.name}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"Tax Plan already exists: {tax_plan.name}")
            )

        # Create multiple TaxCollection entries
        for i in range(1, 6):
            receipt_number = f"RCPT-2025-{i:04d}"

            if TaxCollection.objects.filter(receipt_number=receipt_number).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"TaxCollection {receipt_number} already exists! Skipping."
                    )
                )
                continue

            collection = TaxCollection.objects.create(
                tax_plan=tax_plan,
                amount_paid=1000.00 + i * 100,
                receipt_number=receipt_number,
                collected_by=user,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created TaxCollection: {collection.receipt_number}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Dummy data populated successfully!"))
