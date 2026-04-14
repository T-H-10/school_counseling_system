from core.models import Counselor


class CounselorRepository:

    @staticmethod
    def create(**data):
        return Counselor.objects.create(**data)

    @staticmethod
    def get_by_user(user):
        return Counselor.objects.get(user=user)

    @staticmethod
    def get_by_id(counselor_id):
        return Counselor.objects.get(id=counselor_id)

    @staticmethod
    def update(counselor, data):
        for attr, value in data.items():
            setattr(counselor, attr, value)
        counselor.save()
        return counselor

    @staticmethod
    def delete(counselor):
        counselor.delete()