from core.models import StudentEvent


class StudentEventRepository:

    @staticmethod
    def create(**data):
        return StudentEvent.objects.create(**data)

    @staticmethod
    def get_by_id(user, event_id):
        return StudentEvent.objects.filter(id=event_id).first()
    
    @staticmethod
    def get_all():
        return StudentEvent.objects.all()

    @staticmethod
    def update(event, **data):
        for attr, value in data.items():
            setattr(event, attr, value)
        event.save()
        return event

    @staticmethod
    def delete(event):
        event.delete()