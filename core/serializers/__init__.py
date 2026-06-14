"""Serializers for the ``core`` app.

Split into per-domain modules; this package re-exports every serializer so
existing import paths (``from core.serializers import StudentSerializer``)
keep working.
"""

from .admin import (
    SchoolSerializer,
    ClassLevelSerializer,
    SchoolYearSerializer,
    CounselorSerializer,
)
from .student import (
    StudentSerializer,
    StudentEnrollmentSerializer,
    StudentEventSerializer,
)
from .lesson import (
    LessonClassAssignmentSerializer,
    LessonPlanSerializer,
)

__all__ = [
    "SchoolSerializer",
    "ClassLevelSerializer",
    "SchoolYearSerializer",
    "CounselorSerializer",
    "StudentSerializer",
    "StudentEnrollmentSerializer",
    "StudentEventSerializer",
    "LessonClassAssignmentSerializer",
    "LessonPlanSerializer",
]
