from datetime import timedelta
from django.db.models import Max, Q
from django.utils import timezone

from core.models import LessonClassAssignment, Student, StudentEvent

class DashboardService:

    @staticmethod
    def get_dashboard(user):
        counselor = user.counselor
        now = timezone.now()

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        week_ago = now - timedelta(days=7)
        cutoff_90 = now - timedelta(days=90)

        today_sessions = LessonClassAssignment.objects.filter(
            lesson__counselor=counselor,
            planned_date__range=(today_start, today_end)
        ).select_related("lesson").order_by("planned_date")

        recent_events = StudentEvent.objects.filter(
            counselor=counselor,
            date__gte=week_ago,
            date__lte=now,
        ).order_by("-date").select_related("student")[:5]

        students_count = Student.objects.filter(
            school=counselor.school
        ).count()

        event_this_week = StudentEvent.objects.filter(
            counselor=counselor,
            date__gte=week_ago
        ).count()

        upcoming_today_events = StudentEvent.objects.filter(
            counselor=counselor,
            date__range=(today_start, today_end),
        ).select_related('student').order_by('date')

        next_7_days = now + timedelta(days=7)
        upcoming_future_events = StudentEvent.objects.filter(
            counselor=counselor,
            date__gt=today_end,
            date__lte=next_7_days,
        ).select_related('student').order_by('date')[:5]

        missing_summaries = StudentEvent.objects.filter(
            counselor=counselor,
            date__lt=now,
        ).filter(
            Q(description__isnull=True) | Q(description='')
        ).select_related('student').order_by('-date')[:10]

        at_risk_90 = (
            Student.objects.filter(school=counselor.school)
            .annotate(last_event=Max('events__date', filter=Q(events__counselor=counselor)))
            .filter(Q(last_event__isnull=True) | Q(last_event__lt=cutoff_90))
            .distinct()
        )

        return {
            "today_sessions": [
                {"id": s.id, "title": s.lesson.title, "date": s.planned_date}
                for s in today_sessions
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
                "upcoming_today": [
                    {
                        "id":           str(e.id),
                        "title":        e.title,
                        "date":         e.date,
                        "student_id":   str(e.student.id),
                        "student_name": e.student.full_name,
                        "event_type":   e.event_type,
                        "status":       e.status,
                    }
                    for e in upcoming_today_events
                ],
                "upcoming_future": [
                    {
                        "id":           str(e.id),
                        "title":        e.title,
                        "date":         e.date,
                        "student_id":   str(e.student.id),
                        "student_name": e.student.full_name,
                        "event_type":   e.event_type,
                    }
                    for e in upcoming_future_events
                ],
                "missing_summaries": [
                    {
                        "id": str(e.id),
                        "title": e.title,
                        "date": e.date,
                        "student_id": str(e.student.id),
                        "student_name": e.student.full_name,
                    }
                    for e in missing_summaries
                ],
                "at_risk_students": {
                    "count": at_risk_90.count(),
                    "students": [
                        {"id": str(s.id), "full_name": s.full_name}
                        for s in at_risk_90[:10]
                    ],
                },
            },
        }