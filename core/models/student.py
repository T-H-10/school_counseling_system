from django.db import models
from django.utils import timezone

from core.validators import validate_id_number

from .academic import ClassLevel, SchoolYear
from .base import BaseModel
from .school import Counselor, School


class Student(BaseModel):
    PARENTS_STATUS_CHOICES = [
        ("married",       "נשואים"),
        ("divorced",      "גרושים"),
        ("separated",     "פרודים"),
        ("single_parent", "חד הוריות"),
        ("widowed",       "שכול"),
        ("other",         "אחר"),
    ]

    GENDER_CHOICES = [
        ("male",   "זכר"),
        ("female", "נקבה"),
    ]

    FOLLOW_UP_CHOICES = [
        ("none",       "רגיל"),
        ("monitoring", "במעקב"),
        ("at_risk",    "בסיכון"),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students")

    full_name = models.CharField(max_length=150)
    id_number = models.CharField(max_length=9, unique=True, validators=[validate_id_number])

    address = models.CharField(max_length=255, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)

    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)

    parents_status = models.CharField(
        max_length=20, choices=PARENTS_STATUS_CHOICES, blank=True, default=""
    )
    notes = models.TextField(blank=True, default="")

    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default="")

    guardian_name = models.CharField(max_length=100, blank=True, default="")
    guardian_relation = models.CharField(max_length=50, blank=True, default="")
    guardian_phone = models.CharField(max_length=20, blank=True, default="")

    external_care = models.TextField(blank=True, default="")
    follow_up_level = models.CharField(
        max_length=20, choices=FOLLOW_UP_CHOICES, default="none"
    )

    def __str__(self):
        return self.full_name

    class Meta:
        indexes = [
            models.Index(fields=["school"]),
            models.Index(fields=["id_number"]),
        ]


class StudentEnrollment(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.CASCADE, related_name="enrollments"
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True)
    class_number = models.PositiveIntegerField()
    teacher_name = models.CharField(max_length=150, blank=True, default="")

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.school_year}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "school_year"], name="unique_enrollment_per_year"
            )
        ]


class StudentEvent(BaseModel):
    EVENT_TYPES = [
        ("meeting", "פגישה"),
        ("call", "שיחה"),
        ("teacher_report", "דיווח מורה"),
        ("other", "אחר"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="events")
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name="events")

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)

    title = models.CharField(max_length=200)
    agenda = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    STATUS_CHOICES = [
        ("pending", "ממתין"),
        ("completed", "הושלם"),
    ]

    date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.student.full_name} - {self.event_type}"
