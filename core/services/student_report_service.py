import re
from datetime import datetime

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.helpers import ensure_same_school
from core.models import Document
from core.serializers import StudentSerializer
from core.services.student_timeline_service import StudentTimelineService

YEAR_NAME_RE = re.compile(r"^(\d{4})-(\d{4})$")

# Gematria values for Hebrew letters (final forms map to their regular values).
GEMATRIA = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400,
}
QUOTE_CHARS = "\"'׳״"


def _first_gregorian_year(name):
    """The Gregorian year in which the school year starts, or None.

    Supports both "2025-2026" and Hebrew year names like תשפו / תשפ״ו
    (Hebrew year 5786 starts in autumn 2025 → school year Sep 2025 – Aug 2026).
    """
    name = name.strip()
    match = YEAR_NAME_RE.match(name)
    if match:
        return int(match.group(1))
    # Optional thousands prefix (ה׳תשפו) — drop the leading ה + geresh.
    if len(name) >= 2 and name[0] == "ה" and name[1] in "׳'":
        name = name[2:]
    letters = [c for c in name if c not in QUOTE_CHARS]
    if not letters or any(c not in GEMATRIA for c in letters):
        return None
    hebrew_year = sum(GEMATRIA[c] for c in letters)
    if hebrew_year < 1000:  # millennium digit is customarily omitted (תשפו = 5786)
        hebrew_year += 5000
    return hebrew_year - 3761


class StudentReportService:
    @staticmethod
    def year_date_range(school_year):
        """Derive the date range of an Israeli school year: Sep 1 of its first
        Gregorian year through Aug 31 of the next (Asia/Jerusalem)."""
        first = _first_gregorian_year(school_year.name)
        if first is None:
            raise ValidationError({"year": ["פורמט שנת הלימודים אינו תקין"]})
        tz = timezone.get_default_timezone()
        start = timezone.make_aware(datetime(first, 9, 1), tz)
        end = timezone.make_aware(datetime(first + 1, 8, 31, 23, 59, 59, 999999), tz)
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
