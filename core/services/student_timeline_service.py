from core.models import StudentEvent


class StudentTimelineService:
    @staticmethod
    def get_timeline(student):
        events = StudentEvent.objects.filter(student=student)

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
            }
            for e in events
        ]

        timeline.sort(key=lambda x: x["date"], reverse=True)

        return timeline
