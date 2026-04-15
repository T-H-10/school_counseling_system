from core.models import Student, Counselor
from core.repositories.student_event_repository import StudentEventRepository


class StudentEventService:

    @staticmethod
    def create_event(user, data):

        counselor = user.counselor
        school = counselor.school
        student = data["student"]

        if student.school != school:
            raise PermissionError("Student does not belong to your school")
        
        return StudentEventRepository.create(
            student=student,
            counselor=counselor,
            event_type=data["event_type"],
            title=data["title"],
            description=data["description"],
            school = school
        )

    @staticmethod
    def update_event(user, event_id, data):

        event = StudentEventRepository.get_by_id(event_id)

        if event.school != user.counselor.school:
            raise PermissionError("Not allowed")
        
        data.pop("school", None)
        data.pop("counselor", None)
        data.pop("student", None)

        return StudentEventRepository.update(event, **data)

    @staticmethod
    def delete_event(user, event_id):

        event = StudentEventRepository.get_by_id(event_id)

        if event.school != user.counselor.school:
            raise PermissionError("Not allowed")

        StudentEventRepository.delete(event)