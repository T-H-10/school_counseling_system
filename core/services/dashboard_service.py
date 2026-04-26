from datetime import timedelta
from django.utils import timezone

from core.models import ClassSession, Student, StudentEvent

class DashboardService:

    @staticmethod
    def get_dashboard(user):
        counselor = user.counselor
        now = timezone.now()

        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = now.replace(hour=23, minute=59, second=59)

        week_ago = now - timedelta(days=7)

        today_sessions = ClassSession.objects.filter(
            counselor = counselor,
            date__range=(today_start, today_end)
        )

        recent_events = StudentEvent.objects.filter(
            counselor=counselor, 
            date__gte = week_ago
        ).order_by("-date")[:5]

        students_count = Student.objects.filter(
            school=counselor.school
        ).count()

        event_this_week = StudentEvent.objects.filter(
            counselor=counselor,
            date__gte=week_ago
        ).count()

        return {
            "today_sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "date": s.date,
                }
                for s in today_sessions
            ],
            "recent_events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "date": e.date,
                    "student_id": e.student.id
                }
                for e in recent_events
            ],
            "stats": {
                "students_count": students_count,
                "events_this_week": event_this_week
            }
        }