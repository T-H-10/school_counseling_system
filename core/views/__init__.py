"""View layer for the ``core`` app.

Split into per-domain modules; this package re-exports every ViewSet/View so
existing import paths (``from core.views import StudentViewSet``) keep working.
"""

from .base import BaseSchoolViewSet
from .student import StudentViewSet
from .enrollment import StudentEnrollmentViewSet
from .student_event import StudentEventViewSet
from .lesson import LessonPlanViewSet, LessonClassAssignmentViewSet
from .admin import (
    SchoolViewSet,
    ClassLevelViewSet,
    SchoolYearViewSet,
    CounselorViewSet,
)
from .dashboard import DashboardView
from .document import DocumentViewSet

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
