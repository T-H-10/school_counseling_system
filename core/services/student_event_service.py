from core.helpers import ensure_same_school
from core.repositories.student_event_repository import StudentEventRepository


class StudentEventService:

    @staticmethod
    def create_event(user, data):

        counselor = user.counselor
        student = data["student"]

        ensure_same_school(user, student)
        
        return StudentEventRepository.create(
            student=student,
            counselor=counselor,
            event_type=data["event_type"],
            title=data["title"],
            description=data["description"],
            school = counselor.school
        )

    @staticmethod
    def update_event(user, event, data):

        ensure_same_school(user, event)
        
        data.pop("school", None)
        data.pop("counselor", None)
        data.pop("student", None)

        return StudentEventRepository.update(event, **data)

    @staticmethod
    def delete_event(user, event):

        ensure_same_school(user, event)

        return StudentEventRepository.delete(event)