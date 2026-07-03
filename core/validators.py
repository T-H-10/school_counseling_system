import os
import re

from django.conf import settings
from rest_framework.exceptions import ValidationError

_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".txt",
}

# Magic-byte signatures per extension family. The extension alone is spoofable
# (renaming malicious.exe to report.pdf); the leading bytes are not.
_SIGNATURES = {
    ".pdf": (b"%PDF",),
    ".png": (b"\x89PNG",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".gif": (b"GIF87a", b"GIF89a"),
    ".docx": (b"PK\x03\x04",),  # OOXML = ZIP container
    ".xlsx": (b"PK\x03\x04",),
    ".pptx": (b"PK\x03\x04",),
    ".doc": (b"\xd0\xcf\x11\xe0",),  # legacy Office = OLE2 container
    ".xls": (b"\xd0\xcf\x11\xe0",),
    ".ppt": (b"\xd0\xcf\x11\xe0",),
}


def _content_matches_extension(f, ext):
    # Only the first 1KB is read — never the whole file (a huge upload must
    # not be pulled into memory just to validate it).
    head = f.read(1024)
    f.seek(0)
    if ext == ".txt":
        # NUL bytes never appear in real text; they mark binary content and
        # are a classic null-byte-injection vector.
        return b"\x00" not in head
    return any(head.startswith(sig) for sig in _SIGNATURES[ext])


def validate_document_file(f):
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'סוג הקובץ "{ext}" אינו נתמך.סוגים מותרים: PDF, Word, Excel, PowerPoint, תמונות, טקסט.'
        )
    max_size = settings.DOCUMENT_MAX_UPLOAD_SIZE
    if f.size > max_size:
        mb = max_size // (1024 * 1024)
        raise ValidationError(f"גודל הקובץ חורג מהמקסימום המותר ({mb} MB).")
    if not _content_matches_extension(f, ext):
        raise ValidationError("תוכן הקובץ אינו תואם את סוג הקובץ המוצהר.")


def validate_phone(value):
    if not re.match(r"^05\d{8}$", value):
        raise ValidationError("Invalid phone number")


def validate_id_number(value):
    if not value.isdigit() or len(value) not in (8, 9):
        raise ValidationError("מספר תעודת זהות לא תקין")
    padded = value.zfill(9)
    total = 0
    for i, ch in enumerate(padded):
        product = int(ch) * (1 if i % 2 == 0 else 2)
        total += product - 9 if product >= 10 else product
    if total % 10 != 0:
        raise ValidationError("מספר תעודת זהות לא תקין")


def validate_name(value):
    if len(value) < 2:
        raise ValidationError("Name too short")
