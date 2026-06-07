from datetime import timedelta
from django.db.models import Max
from django.utils import timezone

from core.models import ClassSession, Student, StudentEvent

class DashboardService:

    @staticmethod
    def get_dashboard(user):
        counselor = user.counselor
        now = timezone.now()

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

        week_ago = now - timedelta(days=7)
        cutoff_45 = now - timedelta(days=45)

        today_sessions = ClassSession.objects.filter(
            counselor=counselor,
            date__range=(today_start, today_end)
        ).order_by("date")

        tomorrow_sessions = ClassSession.objects.filter(
            counselor=counselor,
            date__range=(tomorrow_start, tomorrow_end)
        ).order_by("date")

        recent_events = StudentEvent.objects.filter(
            counselor=counselor,
            date__gte=week_ago
        ).order_by("-date").select_related("student")[:5]

        students_count = Student.objects.filter(
            school=counselor.school
        ).count()

        event_this_week = StudentEvent.objects.filter(
            counselor=counselor,
            date__gte=week_ago
        ).count()

        at_risk = (
            Student.objects.filter(
                school=counselor.school,
                events__counselor=counselor,
            )
            .annotate(last_event=Max("events__date"))
            .filter(last_event__lt=cutoff_45)
            .distinct()
        )

        return {
            "today_sessions": [
                {"id": s.id, "title": s.title, "date": s.date}
                for s in today_sessions
            ],
            "tomorrow_sessions": [
                {"id": s.id, "title": s.title, "date": s.date}
                for s in tomorrow_sessions
            ],
            "recent_events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "date": e.date,
                    "student_id": e.student.id,
                    "student_name": e.student.full_name,
                    "event_type": e.event_type,
                }
                for e in recent_events
            ],
            "stats": {
                "students_count": students_count,
                "events_this_week": event_this_week,
            },
            "alerts": {
                "students_without_contact": {
                    "count": at_risk.count(),
                    "students": [
                        {"id": str(s.id), "full_name": s.full_name}
                        for s in at_risk[:10]
                    ],
                }
            },
        }