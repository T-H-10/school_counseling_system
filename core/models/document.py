import os
import uuid

from django.db import models

from core.validators import validate_document_file

from .academic import ClassLevel
from .base import BaseModel
from .school import Counselor, School
from .student import Student


def document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"documents/{uuid.uuid4()}{ext}"


def validate_document_category(category, student, class_level):
    """Return a dict of field-level error messages for an invalid category/relation combo.

    Used by the serializer validate() and mirrors the DB CheckConstraints so the
    rule lives in one place.
    """
    errors = {}
    if category == "student" and not student:
        errors["student"] = "יש לבחור תלמיד עבור מסמך מסוג תלמיד."
    if category == "class" and not class_level:
        errors["class_level"] = "יש לבחור כיתה עבור מסמך מסוג כיתתי."
    if category == "general":
        if student:
            errors["student"] = "מסמך כללי לא יכול להיות משויך לתלמיד."
        if class_level:
            errors["class_level"] = "מסמך כללי לא יכול להיות משויך לכיתה."
    return errors


class Document(BaseModel):
    CATEGORY_CHOICES = [
        ("general", "כללי"),
        ("class", "כיתתי"),
        ("student", "תלמיד"),
    ]

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    counselor = models.ForeignKey(
        Counselor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    file = models.FileField(
        upload_to=document_upload_path,
        validators=[validate_document_file],
    )

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    class_number = models.PositiveSmallIntegerField(null=True, blank=True)

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["school", "category"]),
            models.Index(fields=["student"]),
            models.Index(fields=["class_level", "class_number"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~(models.Q(category="student") & models.Q(student__isnull=True)),
                name="document_student_required_for_student_category",
            ),
            models.CheckConstraint(
                condition=~(models.Q(category="class") & models.Q(class_level__isnull=True)),
                name="document_class_level_required_for_class_category",
            ),
            models.CheckConstraint(
                condition=~(
                    models.Q(category="general")
                    & (models.Q(student__isnull=False) | models.Q(class_level__isnull=False))
                ),
                name="document_general_must_have_no_relations",
            ),
        ]
