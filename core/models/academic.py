from django.db import models
from django.db.models import Q, UniqueConstraint


class ClassLevel(models.Model):
    LEVEL_CHOICES = [
        ("א", "א"),
        ("ב", "ב"),
        ("ג", "ג"),
        ("ד", "ד"),
        ("ה", "ה"),
        ("ו", "ו"),
        ("ז", "ז"),
        ("ח", "ח"),
    ]

    name = models.CharField(max_length=1, choices=LEVEL_CHOICES, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class SchoolYear(models.Model):
    name = models.CharField(max_length=20)  # example: 2025-2026
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="unique_active_school_year",
            )
        ]
