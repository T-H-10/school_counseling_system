from core.models import ClassSession


class ClassSessionRepository:

    @staticmethod
    def create(**data):
        return ClassSession.objects.create(**data)

    @staticmethod
    def get_by_id(session_id):
        return ClassSession.objects.get(id=session_id)

    @staticmethod
    def update(session, **data):
        for attr, value in data.items():
            setattr(session, attr, value)
        session.save()
        return session

    @staticmethod
    def delete(session):
        session.delete()