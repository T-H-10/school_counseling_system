from django.utils.dateparse import parse_datetime

from core.helpers import ensure_same_school
from core.models import LessonPlan, LessonClassAssignment, StudentEvent
from core.services.base import apply_fields


class LessonPlanService:
    @staticmethod
    def create_lesson(user, data):
        counselor = user.counselor

        clean_data = {k: v for k, v in data.items() if k not in ["school", "counselor"]}

        return LessonPlan.objects.create(
            school=counselor.school, counselor=counselor, **clean_data
        )

    @staticmethod
    def update_lesson(user, lesson, data):
        ensure_same_school(user, lesson)
        return apply_fields(lesson, data, exclude=["id", "school", "counselor"])

    @staticmethod
    def delete_lesson(user, lesson):
        ensure_same_school(user, lesson)
        # Soft-delete the lesson and its assignments (archive).
        for assignment in lesson.assignments.all():
            assignment.delete()
        lesson.delete()

    @staticmethod
    def get_calendar(user, start, end):
        counselor = user.counselor

        assignments = LessonClassAssignment.objects.filter(
            school=counselor.school, lesson__counselor=counselor
        ).select_related("class_level", "lesson")

        meetings = StudentEvent.objects.filter(counselor=counselor)

        if start:
            start_dt = parse_datetime(start)
            assignments = assignments.filter(planned_date__gte=start_dt)
            meetings = meetings.filter(date__gte=start_dt)

        if end:
            end_dt = parse_datetime(end)
            assignments = assignments.filter(planned_date__lte=end_dt)
            meetings = meetings.filter(date__lte=end_dt)

        result = []

        for a in assignments:
            if not a.planned_date:
                continue
            label = a.class_level.name
            if a.class_number:
                label = f"{label}{a.class_number}"
            result.append(
                {
                    "id": a.id,
                    "lesson_id": a.lesson.id,
                    "type": "lesson",
                    "title": a.lesson.title,
                    "start": a.planned_date,
                    "end": a.completed_date,
                    "with": label,
                }
            )

        for m in meetings:
            result.append(
                {
                    "id": m.id,
                    "type": "student_event",
                    "title": m.title,
                    "start": m.date,
                    "end": m.end_date,
                    "with": m.student.full_name,
                }
            )

        result.sort(key=lambda x: x["start"], reverse=True)
        return result
