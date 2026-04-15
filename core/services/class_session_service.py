from core.helpers import ensure_same_school
from core.models import ClassSession


class ClassSessionService:

    @staticmethod
    def create_session(user, data):

        counselor = user.counselor

        data.pop("school", None)
        data.pop("counselor", None)

        return ClassSession.objects.create(
            school=counselor.school,
            counselor=counselor,
            school_year=data["school_year"],
            class_level=data["class_level"],
            title=data["title"],
            summary=data["summary"],
            date=data["date"]
        )

    @staticmethod
    def update_session(user, session, data):

        ensure_same_school(user, session)
        
        data.pop("id", None)
        data.pop("school", None)
        data.pop("counselor", None)
        
        for attr, value in data.items():
            setattr(session, attr, value)
        session.save()
        return session

    @staticmethod
    def delete_session(user, session):

        ensure_same_school(user, session)
        session.delete()