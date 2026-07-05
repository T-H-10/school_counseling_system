"""Serializers for the ``core`` app.

Split into per-domain modules; this package re-exports every serializer so
existing import paths (``from core.serializers import StudentSerializer``)
keep working.
"""

from .admin import (
    ArchiveEntrySerializer,
    ClassLevelSerializer,
    CounselorSerializer,
    SchoolSerializer,
    SchoolYearSerializer,
)
from .document import DocumentSerializer
from .support import SupportRequestSerializer
from .lesson import (
    LessonClassAssignmentSerializer,
    LessonPlanSerializer,
)
from .student import (
    StudentEnrollmentSerializer,
    StudentEventSerializer,
    StudentSerializer,
)

__all__ = [
    "SchoolSerializer",
    "ClassLevelSerializer",
    "SchoolYearSerializer",
    "CounselorSerializer",
    "ArchiveEntrySerializer",
    "StudentSerializer",
    "StudentEnrollmentSerializer",
    "StudentEventSerializer",
    "LessonClassAssignmentSerializer",
    "LessonPlanSerializer",
    "DocumentSerializer",
    "SupportRequestSerializer",
]
