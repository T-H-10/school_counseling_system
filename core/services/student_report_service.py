import re
from datetime import datetime

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.helpers import ensure_same_school
from core.models import Document
from core.serializers import StudentSerializer
from core.services.student_timeline_service import StudentTimelineService

YEAR_NAME_RE = re.compile(r"^(\d{4})-(\d{4})$")


class StudentReportService:
    @staticmethod
    def year_date_range(school_year):
        """Derive the date range of an Israeli school year: "2025-2026" runs
        Sep 1 2025 through Aug 31 2026 (Asia/Jerusalem)."""
        match = YEAR_NAME_RE.match(school_year.name)
        if not match:
            raise ValidationError({"year": ["פורמט שנת הלימודים אינו תקין"]})
        first, second = int(match.group(1)), int(match.group(2))
        tz = timezone.get_default_timezone()
        start = timezone.make_aware(datetime(first, 9, 1), tz)
        end = timezone.make_aware(datetime(second, 8, 31, 23, 59, 59, 999999), tz)
        return start, end

    @staticmethod
    def get_report(user, student, school_year=None):
        ensure_same_school(user, student)
        counselor = user.counselor

        start = end = None
        year_filter = None
        if school_year:
            start, end = StudentReportService.year_date_range(school_year)
            year_filter = {"id": school_year.id, "name": school_year.name}

        enrollments = student.enrollments.select_related("school_year", "class_level")
        if school_year:
            enrollments = enrollments.filter(school_year=school_year)
        enrollments = sorted(enrollments, key=lambda e: e.school_year.name, reverse=True)

        documents = Document.objects.filter(student=student, category="student")
        if start:
            documents = documents.filter(created_at__range=(start, end))
        documents = documents.order_by("-created_at")

        return {
            "generated_at": timezone.now(),
            "school": {
                "name": counselor.school.name,
                "institution_code": counselor.school.institution_code,
            },
            "counselor": {"full_name": counselor.full_name},
            "year_filter": year_filter,
            "student": StudentSerializer(student).data,
            "enrollments": [
                {
                    "id": e.id,
                    "school_year_name": e.school_year.name,
                    "class_level_name": e.class_level.name if e.class_level else None,
                    "class_number": e.class_number,
                    "teacher_name": e.teacher_name,
                }
                for e in enrollments
            ],
            "events": StudentTimelineService.get_timeline(student, start=start, end=end),
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "created_at": d.created_at,
                    "display_date": timezone.localtime(d.created_at).strftime("%d/%m/%Y"),
                }
                for d in documents
            ],
        }
