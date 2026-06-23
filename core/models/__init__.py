"""Data model for the ``core`` app.

Split into per-domain modules; this package re-exports every model (and the
soft-delete base classes) so existing import paths
(``from core.models import Student``) keep working. Import order follows the
foreign-key dependency chain.
"""

from .academic import ClassLevel, SchoolYear
from .base import BaseManager, BaseModel, BaseQuerySet, SoftDeleteModel
from .document import Document
from .lesson import LessonClassAssignment, LessonPlan
from .school import Counselor, School
from .student import Student, StudentEnrollment, StudentEvent

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
