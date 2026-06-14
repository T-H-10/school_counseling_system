from django.db import models

from .base import BaseModel
from .school import School, Counselor
from .academic import ClassLevel, SchoolYear


class LessonPlan(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="lessons")
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name="lessons")

    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    presentation_url = models.URLField(blank=True, null=True)  # קישור למצגת / Drive

    def __str__(self):
        return self.title


class LessonClassAssignment(BaseModel):
    STATUS_CHOICES = [
        ('planned',   'מתוכנן'),
        ('completed', 'הושלם'),
    ]

    lesson = models.ForeignKey(LessonPlan, on_delete=models.CASCADE, related_name="assignments")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="lesson_assignments")

    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    class_number = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    planned_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        label = self.class_level.name
        if self.class_number:
            label = f"{label}{self.class_number}"
        return f"{self.lesson.title} - {label}"
