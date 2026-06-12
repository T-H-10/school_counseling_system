from core.helpers import ensure_same_school
from core.models import StudentEvent
from core.services.base import apply_fields


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

        return apply_fields(event, data, exclude=["school", "counselor", "student", "id"])
    
    @staticmethod
    def delete_event(user, event):

        ensure_same_school(user, event)

        event.delete()