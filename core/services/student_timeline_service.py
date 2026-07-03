from core.models import StudentEvent


class StudentTimelineService:
    @staticmethod
    def get_timeline(student, start=None, end=None):
        events = StudentEvent.objects.filter(student=student)
        if start:
            events = events.filter(date__gte=start)
        if end:
            events = events.filter(date__lte=end)

        timeline = [
            {
                "id": e.id,
                "type": "event",
                "date": e.date,
                "display_date": e.date.strftime("%d/%m/%Y %H:%M"),
                "title": e.title,
                "agenda": e.agenda,
                "description": e.description,
                "event_type": e.event_type,
                "status": e.status,
            }
            for e in events
        ]

        timeline.sort(key=lambda x: x["date"], reverse=True)

        return timeline
