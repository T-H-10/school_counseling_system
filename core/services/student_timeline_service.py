from itertools import chain
from django.utils import timezone
from core.models import ClassSession

class StudentTimelineService:

    @staticmethod
    def get_timeline(student):

        events = StudentTimelineService._events(student)
        sessions = StudentTimelineService._sessions(student)

        combined = sorted(
            chain(events, sessions),
            key=lambda x: x["date"],
            reverse=True
        )

        return combined

    @staticmethod
    def _events(student):
        return [
            {
                "type": "event",
                "date": e.created_at,
                "title": e.title,
                "description": e.description,
                "scope": "personal"
            }
            for e in student.events.all().select_related("counselor")
        ]

    @staticmethod
    def _sessions(student):

        enrollments = student.enrollments.all()

        # נבנה פילטר אחד חכם במקום לולאות כבדות
        sessions = ClassSession.objects.filter(
            school=student.school,
            school_year__in=[e.school_year for e in enrollments],
            class_level__in=[e.class_level for e in enrollments],
        ).select_related("counselor", "school_year", "class_level")

        return [
            {
                "type": "session",
                "date": s.date,
                "title": s.title,
                "description": s.summary,
                "scope": "class"
            }
            for s in sessions
        ]