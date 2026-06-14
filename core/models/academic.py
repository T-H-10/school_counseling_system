from django.db import models


class ClassLevel(models.Model):

    LEVEL_CHOICES = [
        ('א', 'א'),
        ('ב', 'ב'),
        ('ג', 'ג'),
        ('ד', 'ד'),
        ('ה', 'ה'),
        ('ו', 'ו'),
        ('ז', 'ז'),
        ('ח', 'ח'),
    ]

    name = models.CharField(max_length=1, choices=LEVEL_CHOICES, unique=True)

    def __str__(self):
        return self.name


class SchoolYear(models.Model):
    name = models.CharField(max_length=20)  # example: 2025-2026
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
