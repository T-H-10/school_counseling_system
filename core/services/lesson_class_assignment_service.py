from core.helpers import ensure_same_school
from core.models import LessonClassAssignment
from core.services.base import apply_fields
from django.utils import timezone


class LessonClassAssignmentService:
    @staticmethod
    def assign_class(user, data):
        lesson = data["lesson"]
        ensure_same_school(user, lesson)

        clean_data = {k: v for k, v in data.items() if k not in ["school"]}

        return LessonClassAssignment.objects.create(school=user.counselor.school, **clean_data)

    @staticmethod
    def update_assignment(user, assignment, data):
        ensure_same_school(user, assignment)
        return apply_fields(assignment, data, exclude=["id", "school", "lesson"])

    @staticmethod
    def complete_assignment(user, assignment, data):
        ensure_same_school(user, assignment)

        assignment.status = "completed"
        assignment.summary = data.get("summary", assignment.summary)
        assignment.completed_date = data.get("completed_date") or timezone.now()
        assignment.save()
        return assignment

    @staticmethod
    def delete_assignment(user, assignment):
        ensure_same_school(user, assignment)
        assignment.delete()
