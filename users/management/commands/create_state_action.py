# your_app/management/commands/create_workflow_samples.py

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from workflow.models import WorkflowAction, WorkflowState

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample WorkflowAction and WorkflowState entries"

    def handle(self, *args, **kwargs):
        # Get or create a default user (replace with your logic)
        user = User.objects.all().first()

        # Create Workflow Actions
        actions = ["Approve", "Reject", "Review"]
        for action_name in actions:
            action, created = WorkflowAction.objects.get_or_create(
                action=action_name, defaults={"created_by": user}
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'{"Created" if created else "Exists"} WorkflowAction: {action_name}'
                )
            )

        # Create Workflow States
        states = [
            ("Approved", "Request has been approved"),
            ("Rejected", "Request has been denied"),
            ("UnderReview", "Request has been denied"),
        ]

        for name, desc in states:
            state, created = WorkflowState.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'{"Created" if created else "Exists"} WorkflowState: {name}'
                )
            )
