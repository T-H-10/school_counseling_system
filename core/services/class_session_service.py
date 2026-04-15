from core.helpers import ensure_same_school
from core.repositories.class_session_repository import ClassSessionRepository


class ClassSessionService:

    @staticmethod
    def create_session(user, data):

        counselor = user.counselor

        return ClassSessionRepository.create(
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
        
        data.pop("school", None)
        data.pop("counselor", None)
        
        return ClassSessionRepository.update(session, **data)

    @staticmethod
    def delete_session(user, session):

        ensure_same_school(user, session)
        return ClassSessionRepository.delete(session)