from django.core.exceptions import ValidationError


def validate_file_type(file):
    valid_mime_types = [
        "application/pdf",
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "image/jpeg",
        "image/png",
        "image/gif",
    ]

    file_mime_type = file.file.content_type

    if file_mime_type not in valid_mime_types:
        raise ValidationError("Unsupported file type.")
