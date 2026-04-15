from django.contrib.auth.models import User
from core.models import School
from core.repositories.counselor_repository import CounselorRepository


class CounselorService:

    @staticmethod
    def create_counselor(request_user, data):

        if not request_user.is_superuser:
            raise PermissionError("Only admin can create counselors")
        
        if User.objects.filter(username=data["username"]).exists():
            raise ValueError("Username already exists")

        username = data.pop("username")
        password = data.pop("password")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        return CounselorRepository.create(
            user=user,
            **data
        )

    @staticmethod
    def update_counselor(request_user, counselor_id, data):

        if not request_user.is_superuser:
            raise PermissionError("Only admin can update counselors")
        
        counselor = CounselorRepository.get_by_id(counselor_id)

        data.pop("user", None)
        data.pop("school", None)

        return CounselorRepository.update(counselor, **data)

    @staticmethod
    def delete_counselor(request_user, counselor_id):

        if not request_user.is_superuser:
            raise PermissionError("Only admin can delete counselors")

        counselor = CounselorRepository.get_by_id(counselor_id)

        CounselorRepository.delete(counselor)

    @staticmethod
    def reset_password(request_user, counselor_id, new_password):

        if not request_user.is_superuser:
            raise PermissionError("Only admin can reset passwords")

        counselor = CounselorRepository.get_by_id(counselor_id)

        user = counselor.user
        user.set_password(new_password)
        user.save()