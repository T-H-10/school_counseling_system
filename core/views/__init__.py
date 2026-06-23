"""View layer for the ``core`` app.

Split into per-domain modules; this package re-exports every ViewSet/View so
existing import paths (``from core.views import StudentViewSet``) keep working.
"""

from .admin import (
    ClassLevelViewSet,
    CounselorViewSet,
    SchoolViewSet,
    SchoolYearViewSet,
)
from .base import BaseSchoolViewSet
from .dashboard import DashboardView
from .document import DocumentViewSet
from .enrollment import StudentEnrollmentViewSet
from .lesson import LessonClassAssignmentViewSet, LessonPlanViewSet
from .student import StudentViewSet
from .student_event import StudentEventViewSet

__all__ = [
    "BaseSchoolViewSet",
    "StudentViewSet",
    "StudentEnrollmentViewSet",
    "StudentEventViewSet",
    "LessonPlanViewSet",
    "LessonClassAssignmentViewSet",
    "SchoolViewSet",
    "ClassLevelViewSet",
    "SchoolYearViewSet",
    "CounselorViewSet",
    "DashboardView",
    "DocumentViewSet",
]
