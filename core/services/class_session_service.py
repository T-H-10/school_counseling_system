from core.models import SchoolYear, ClassLevel
from core.repositories.class_session_repository import ClassSessionRepository


class ClassSessionService:

    @staticmethod
    def create_session(user, data):

        counselor = user.counselor
        school = counselor.school

        return ClassSessionRepository.create(
            school=school,
            counselor=counselor,
            school_year=data["school_year"],
            class_level=data["class_level"],
            title=data["title"],
            summary=data["summary"],
            date=data["date"]
        )

    @staticmethod
    def update_session(user, session, data):

        if session.school != user.counselor.school:
            raise PermissionError("Not allowed")
        
        # data.pop("school", None)
        # data.pop("counselor", None)
        
        return ClassSessionRepository.update(session, **data)

    @staticmethod
    def delete_session(user, session):

        if session.school != user.counselor.school:
            raise PermissionError("Not allowed")

        ClassSessionRepository.delete(session)