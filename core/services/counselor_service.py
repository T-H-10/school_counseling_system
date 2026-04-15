from django.contrib.auth.models import User
from core.models import School
from core.repositories.counselor_repository import CounselorRepository


class CounselorService:

    @staticmethod
    def create_counselor(data):
        
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"]
        )

        school = data["school"]

        return CounselorRepository.create(
            user=user,
            school=school,
            full_name=data["full_name"]
        )

    @staticmethod
    def update_counselor(counselor_id, data):
        counselor = CounselorRepository.get_by_id(counselor_id)
        return CounselorRepository.update(counselor, data)

    @staticmethod
    def delete_counselor(counselor_id):
        counselor = CounselorRepository.get_by_id(counselor_id)
        return CounselorRepository.delete(counselor)