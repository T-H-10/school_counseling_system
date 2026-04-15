from core.helpers import ensure_same_school
from core.models import ClassSession


class ClassSessionService:

    @staticmethod
    def create_session(user, data):

        counselor = user.counselor

        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school", "counselor"]
        }

        return ClassSession.objects.create(
            school=counselor.school,
            counselor=counselor,
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