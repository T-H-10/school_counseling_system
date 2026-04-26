from datetime import timedelta
from core.helpers import ensure_same_school
from core.models import ClassSession
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

        queryset = ClassSession.objects.filter(
            counselor = counselor
        ).select_related("class_level", "counselor")

        if start:
            queryset = queryset.filter(date__gte = parse_datetime(start))

        if end:
            queryset = queryset.filter(date__lte = parse_datetime(end))

        return [
            {
                "id": s.id,
                "title": s.title,
                "start": s.date,
                "end": s.end_date,
                "class_level": s.class_level.name,
                "created_by": s.counselor.full_name,
            }
            for s in queryset
        ]