from core.models import SchoolYear, ClassLevel
from core.repositories.class_session_repository import ClassSessionRepository


class ClassSessionService:

    @staticmethod
    def create_session(user, data):

        if not hasattr(user, "counselor"):
            raise ValueError("User is not a counselor")

        counselor = user.counselor
        school = counselor.school

        school_year = SchoolYear.objects.get(id=data["school_year"])
        class_level = ClassLevel.objects.get(id=data["class_level"])

        return ClassSessionRepository.create(
            school=school,
            counselor=counselor,
            school_year=school_year,
            class_level=class_level,
            title=data["title"],
            summary=data["summary"],
            date=data["date"]
        )

    @staticmethod
    def update_session(user, session_id, data):

        if not hasattr(user, "counselor"):
            raise ValueError("User is not a counselor")

        session = ClassSessionRepository.get_by_id(user, session_id)

        return ClassSessionRepository.update(session, data)

    @staticmethod
    def delete_session(user, session_id):

        if not hasattr(user, "counselor"):
            raise ValueError("User is not a counselor")

        session = ClassSessionRepository.get_by_id(user, session_id)

        ClassSessionRepository.delete(session)