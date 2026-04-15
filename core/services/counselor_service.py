from django.contrib.auth.models import User
from django.db import transaction

from core.repositories.counselor_repository import CounselorRepository


class CounselorService:

    @staticmethod
    @transaction.atomic
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
        
        data.pop("user", None)
        data.pop("school", None)
        data.pop("id", None)

        return CounselorRepository.update(counselor, **data)

    @staticmethod
    @transaction.atomic
    def delete_counselor(counselor):

        user = counselor.user
        CounselorRepository.delete(counselor)
        user.delete()

    @staticmethod
    def reset_password(counselor, new_password):

        user = counselor.user
        user.set_password(new_password)
        user.save()