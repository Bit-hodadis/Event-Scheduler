import os
from datetime import datetime
from uuid import uuid4


def uploadTo(instance, filename):
    # Extract the file extension
    ext = filename.split(".")[-1]
    # Generate a unique filename using UUID
    unique_filename = f"{uuid4().hex}.{ext}"

    # Optional: Organize by date
    date_path = datetime.now().strftime("%Y/%m/%d")

    # Construct the final upload path
    return os.path.join(
        "posts",
        instance.__class__.__name__.lower(),
        str(instance.pk)
        or "unassigned",  # Instance ID or 'unassigned' if instance hasn't been saved yet
        date_path,
        unique_filename,
    )
