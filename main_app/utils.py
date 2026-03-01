import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage


ALLOWED_UPLOAD_EXTENSIONS = getattr(
    settings, 'ALLOWED_UPLOAD_EXTENSIONS',
    ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
)
MAX_UPLOAD_SIZE = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)  # 5MB


def validate_file_upload(uploaded_file):
    """Validate file extension and size. Raises ValidationError if invalid."""
    if uploaded_file is None:
        return None

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(
            f"File type '{ext}' is not allowed. Allowed types: {', '.join(ALLOWED_UPLOAD_EXTENSIONS)}"
        )

    if uploaded_file.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File size exceeds the maximum allowed size of {MAX_UPLOAD_SIZE // (1024*1024)}MB."
        )

    return uploaded_file


def handle_file_upload(uploaded_file):
    """Validate, rename with UUID, and save the uploaded file. Returns the URL."""
    validate_file_upload(uploaded_file)
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    new_filename = f"{uuid.uuid4().hex}{ext}"
    fs = FileSystemStorage()
    filename = fs.save(new_filename, uploaded_file)
    return fs.url(filename)
