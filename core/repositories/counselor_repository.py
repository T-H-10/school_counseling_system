from core.models import Counselor


class CounselorRepository:

    @staticmethod
    def create(**data):
        return Counselor.objects.create(**data)

    @staticmethod
    def get_by_user(user):
        return Counselor.objects.filter(user=user).first()
    
    @staticmethod
    def get_all():
        return Counselor.objects.all()

    @staticmethod
    def get_by_id(counselor_id):
        return Counselor.objects.filter(id=counselor_id).first()

    @staticmethod
    def update(counselor, **data):
        for attr, value in data.items():
            setattr(counselor, attr, value)
        counselor.save()
        return counselor

    @staticmethod
    def delete(counselor):
        counselor.delete()