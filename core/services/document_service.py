from django.db import transaction

from core.helpers import ensure_same_school
from core.models import Document
from core.services.base import apply_fields


class DocumentService:
    @staticmethod
    def create_document(user, data):
        counselor = user.counselor
        school = counselor.school

        student = data.get("student")
        if student:
            ensure_same_school(user, student)

        clean_data = {k: v for k, v in data.items() if k not in ("school", "counselor")}

        return Document.objects.create(
            counselor=counselor,
            school=school,
            **clean_data,
        )

    @staticmethod
    def update_document(user, doc, data):
        ensure_same_school(user, doc)

        student = data.get("student")
        if student:
            ensure_same_school(user, student)

        new_file = data.get("file")
        old_file = doc.file if new_file else None

        with transaction.atomic():
            apply_fields(doc, data, exclude=["school", "counselor", "id"])

        # Delete the replaced file only after the DB save committed (C3).
        if old_file and new_file and old_file.name != new_file.name:
            old_file.delete(save=False)

        return doc

    @staticmethod
    def delete_document(user, doc):
        ensure_same_school(user, doc)
        doc.delete()
