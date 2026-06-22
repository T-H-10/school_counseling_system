import os
import re

from django.conf import settings
from rest_framework.exceptions import ValidationError

_ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.png', '.jpg', '.jpeg', '.gif', '.txt',
}

def validate_document_file(f):
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValidationError(f'סוג הקובץ "{ext}" אינו נתמך. סוגים מותרים: PDF, Word, Excel, PowerPoint, תמונות, טקסט.')
    max_size = settings.DOCUMENT_MAX_UPLOAD_SIZE
    if f.size > max_size:
        mb = max_size // (1024 * 1024)
        raise ValidationError(f'גודל הקובץ חורג מהמקסימום המותר ({mb} MB).')


def validate_phone(value):
    if not re.match(r'^05\d{8}$', value):
        raise ValidationError("Invalid phone number")


def validate_id_number(value):
    if not value.isdigit() or len(value) not in [8, 9]:
        raise ValidationError("Invalid ID number")


def validate_name(value):
    if len(value) < 2:
        raise ValidationError("Name too short")