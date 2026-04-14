from core.models import Student, Counselor
from core.repositories.student_event_repository import StudentEventRepository


class StudentEventService:

    @staticmethod
    def create_event(user, data):

        counselor = user.counselor
        school = counselor.school

        student = Student.objects.for_user(user).get(id=data["student"])

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

        event = StudentEventRepository.get_by_id(user, event_id)

        return StudentEventRepository.update(event, data)

    @staticmethod
    def delete_event(user, event_id):

        event = StudentEventRepository.get_by_id(user, event_id)

        StudentEventRepository.delete(event)