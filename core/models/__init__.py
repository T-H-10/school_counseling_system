"""Data model for the ``core`` app.

Split into per-domain modules; this package re-exports every model (and the
soft-delete base classes) so existing import paths
(``from core.models import Student``) keep working. Import order follows the
foreign-key dependency chain.
"""

from .base import SoftDeleteModel, BaseQuerySet, BaseManager, BaseModel
from .school import School, Counselor
from .academic import ClassLevel, SchoolYear
from .student import Student, StudentEnrollment, StudentEvent
from .lesson import LessonPlan, LessonClassAssignment
from .document import Document

__all__ = [
    "SoftDeleteModel",
    "BaseQuerySet",
    "BaseManager",
    "BaseModel",
    "School",
    "Counselor",
    "ClassLevel",
    "SchoolYear",
    "Student",
    "StudentEnrollment",
    "StudentEvent",
    "LessonPlan",
    "LessonClassAssignment",
    "Document",
]
