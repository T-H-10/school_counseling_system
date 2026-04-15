from core.models import StudentEvent


class StudentEventRepository:

    @staticmethod
    def create(**data):
        return StudentEvent.objects.create(**data)

    @staticmethod
    def get_by_id(user, event_id):
        return StudentEvent.objects.get(id=event_id)

    @staticmethod
    def update(event, **data):
        for attr, value in data.items():
            setattr(event, attr, value)
        event.save()
        return event

    @staticmethod
    def delete(event):
        event.delete()