from datetime import timedelta
from core.helpers import ensure_same_school
from core.models import ClassSession, StudentEvent
from django.utils.dateparse import parse_datetime

class ClassSessionService:

    @staticmethod
    def create_session(user, data):

        counselor = user.counselor

        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school", "counselor", "end_date"]
        }

        date = clean_data["date"]
        end_date = data.get("end_date")
        if not end_date:
            end_date = date + timedelta(minutes=45)

        return ClassSession.objects.create(
            school=counselor.school,
            counselor=counselor,
            end_date=end_date,
            **clean_data
        )

    @staticmethod
    def update_session(user, session, data):

        ensure_same_school(user, session)
        
        clean_data = {
            k: v for k, v in data.items()
            if k not in ["id", "school", "counselor"]
        }
        
        for attr, value in clean_data.items():
            setattr(session, attr, value)
        session.save()
        return session

    @staticmethod
    def delete_session(user, session):

        ensure_same_school(user, session)
        session.delete()

    @staticmethod
    def get_calendar(user, start, end):
        counselor = user.counselor

        sessions = ClassSession.objects.filter(
            counselor = counselor
        ).select_related("class_level", "counselor")

        meetings = StudentEvent.objects.filter(
            counselor=counselor
        )
        if start:
            sessions = sessions.filter(date__gte = parse_datetime(start))
            meetings = meetings.filter(date__gte = parse_datetime(start))

        if end:
            queryset = queryset.filter(date__lte = parse_datetime(end))
            meetings = meetings.filter(date__lte = parse_datetime(end))

        result = []

        for s in sessions:
            result.append(
            {
                "id": s.id,
                "type": "class_session",
                "title": s.title,
                "start": s.date,
                "end": s.end_date,
                "with": s.class_level.name,
            }
        )
        
        for m in meetings:
            result.append({
                "id": m.id,
                "type": "student_event",
                "title": m.title,
                "start": m.date,
                "end": m.end_date,
                "with": m.class_level.name,
            })

        result.sort(key=lambda x: x["start"], reverse=True)
        return result