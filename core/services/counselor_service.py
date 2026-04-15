from django.contrib.auth.models import User
from core.models import School
from core.repositories.counselor_repository import CounselorRepository


class CounselorService:

    @staticmethod
    def create_counselor(data):

        username = data["username"]
        password = data["password"]
        school = data["school"]

        if User.objects.filter(username=data["username"]).exists():
            raise ValueError("Username already exists")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        return CounselorRepository.create(
            user=user,
            school = school,
            full_name = data["full_name"]
        )
    

    @staticmethod
    def update_counselor(counselor, data):

        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin can update counselors")
        
        data.pop("user", None)
        data.pop("school", None)

        return CounselorRepository.update(counselor, **data)

    @staticmethod
    def delete_counselor(counselor):

        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin can delete counselors")

        CounselorRepository.delete(counselor)

    @staticmethod
    def reset_password(counselor, new_password):

        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin can reset passwords")

        user = counselor.user
        user.set_password(new_password)
        user.save()