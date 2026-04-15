from core.helpers import ensure_same_school
from core.models import StudentEvent


class StudentEventService:

    @staticmethod
    def create_event(user, data):

        counselor = user.counselor
        student = data["student"]

        ensure_same_school(user, student)
        
        data.pop("school", None)
        data.pop("counselor", None)
        
        return StudentEvent.objects.create(
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
        data.pop("id", None)

        for attr, value in data.items():
            setattr(event, attr, value)
        event.save()
        return event
    
    @staticmethod
    def delete_event(user, event):

        ensure_same_school(user, event)

        event.delete()