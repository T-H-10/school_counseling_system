"""Admin-only archive/restore for the 5 soft-deletable entities.

Uses the ``all_objects`` manager defined on ``BaseModel`` (unfiltered by
``deleted_at``) which nothing else in the app touches — every other view/
service goes through the default ``objects`` manager that hides soft-deleted
rows entirely.
"""

from core.models import LessonClassAssignment, LessonPlan, Student, StudentEnrollment, StudentEvent

ENTITY_MODELS = {
    "students": Student,
    "enrollments": StudentEnrollment,
    "studentEvents": StudentEvent,
    "lessons": LessonPlan,
    "lessonAssignments": LessonClassAssignment,
}

# entity_type -> (fk_field_name, parent_model), for entities whose restore
# must not resurrect a row pointing at a still-deleted parent. Entity types
# absent here have no parent (top of their hierarchy).
PARENT_FK = {
    "enrollments": ("student", Student),
    "studentEvents": ("student", Student),
    "lessonAssignments": ("lesson", LessonPlan),
}

BLOCKED_REASONS = {
    "enrollments": "יש לשחזר קודם את התלמיד המקושר",
    "studentEvents": "יש לשחזר קודם את התלמיד המקושר",
    "lessonAssignments": "יש לשחזר קודם את השיעור המקושר",
}

# Relations each entity's __str__ (used as display_label) and school_name
# dereference. select_related-ing them up front avoids two problems at once:
# an N+1 query per row, and a real Django gotcha — BaseModel's default
# (soft-delete-filtered) manager doubles as the model's `_base_manager`
# (the first manager declared), which Django uses internally whenever a
# forward FK descriptor lazily fetches an uncached related object. So
# `event.student` would raise Student.DoesNotExist if `student` were
# soft-deleted and not already cached. select_related() populates that cache
# via our own `all_objects`-based query instead, sidestepping the trap for
# exactly the orphaned rows this feature needs to display safely.
DISPLAY_RELATED = {
    "students": ["school"],
    "enrollments": ["school", "student", "school_year"],
    "studentEvents": ["school", "student"],
    "lessons": ["school"],
    "lessonAssignments": ["school", "lesson", "class_level"],
}


class ArchiveIntegrityError(Exception):
    """Raised when restoring a row would orphan it under a still-deleted parent."""

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


class ArchiveService:
    @staticmethod
    def list_archived(entity_type, school=None, deleted_after=None, deleted_before=None):
        model = ENTITY_MODELS[entity_type]
        qs = model.all_objects.filter(deleted_at__isnull=False)
        qs = qs.select_related(*DISPLAY_RELATED[entity_type])
        if school:
            qs = qs.filter(school=school)
        if deleted_after:
            qs = qs.filter(deleted_at__gte=deleted_after)
        if deleted_before:
            qs = qs.filter(deleted_at__lte=deleted_before)
        return qs.order_by("-deleted_at")

    @staticmethod
    def _alive_parent_ids(entity_type, rows):
        """One bulk query for the whole page's parent liveness — not per row."""
        parent = PARENT_FK.get(entity_type)
        if parent is None:
            return None
        field_name, parent_model = parent
        parent_ids = {getattr(row, f"{field_name}_id") for row in rows}
        return set(parent_model.objects.filter(pk__in=parent_ids).values_list("pk", flat=True))

    @staticmethod
    def _restorability(entity_type, instance, alive_parent_ids):
        parent = PARENT_FK.get(entity_type)
        if parent is None:
            return True, None
        field_name, _ = parent
        parent_id = getattr(instance, f"{field_name}_id")
        if alive_parent_ids is not None and parent_id in alive_parent_ids:
            return True, None
        return False, BLOCKED_REASONS[entity_type]

    @staticmethod
    def _serialize_row(entity_type, instance, alive_parent_ids):
        is_restorable, blocked_reason = ArchiveService._restorability(
            entity_type, instance, alive_parent_ids
        )
        return {
            "id": instance.id,
            "entity_type": entity_type,
            "display_label": str(instance),
            "school_name": instance.school.name,
            "deleted_at": instance.deleted_at,
            "created_at": instance.created_at,
            "is_restorable": is_restorable,
            "blocked_reason": blocked_reason,
        }

    @staticmethod
    def serialize_list(entity_type, rows):
        alive_parent_ids = ArchiveService._alive_parent_ids(entity_type, rows)
        return [ArchiveService._serialize_row(entity_type, row, alive_parent_ids) for row in rows]

    @staticmethod
    def serialize_one(entity_type, instance):
        alive_parent_ids = ArchiveService._alive_parent_ids(entity_type, [instance])
        return ArchiveService._serialize_row(entity_type, instance, alive_parent_ids)

    @staticmethod
    def restore(entity_type, pk):
        """Undo a soft delete. Restore-only — no hard-delete is ever exposed.

        Raises the model's DoesNotExist if ``pk`` isn't found, or
        ArchiveIntegrityError if the parent (when there is one) is still
        soft-deleted — restoring the child first would leave it pointing at a
        "deleted" parent.
        """
        model = ENTITY_MODELS[entity_type]
        instance = model.all_objects.get(pk=pk)
        parent = PARENT_FK.get(entity_type)
        if parent is not None:
            field_name, parent_model = parent
            parent_id = getattr(instance, f"{field_name}_id")
            if not parent_model.objects.filter(pk=parent_id).exists():
                raise ArchiveIntegrityError(BLOCKED_REASONS[entity_type])
        instance.deleted_at = None
        instance.save(update_fields=["deleted_at"])
        return instance

    @staticmethod
    def counts_by_entity(school=None):
        return {key: ArchiveService.list_archived(key, school=school).count() for key in ENTITY_MODELS}
