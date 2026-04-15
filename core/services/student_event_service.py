from core.helpers import ensure_same_school
from core.models import StudentEvent


class StudentEventService:

    @staticmethod
    def create_event(user, data):

        counselor = user.counselor
        student = data["student"]

        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school", "counselor"]
        }

        ensure_same_school(user, student)
        
        
        return StudentEvent.objects.create(
            counselor=counselor,
            school = counselor.school,
            **clean_data
        )

    @staticmethod
    def update_event(user, event, data):

        ensure_same_school(user, event)
        
        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school", "counselor", "student", "id"]
        }

        for attr, value in clean_data.items():
            setattr(event, attr, value)
        event.save()
        return event
    
    @staticmethod
    def delete_event(user, event):

        ensure_same_school(user, event)

        event.delete()