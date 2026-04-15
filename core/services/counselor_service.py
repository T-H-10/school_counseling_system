from django.contrib.auth.models import User
from django.db import transaction

from core.models import Counselor


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

        return Counselor.objects.create(
            user=user,
            school = school,
            full_name = data["full_name"]
        )
    

    @staticmethod
    def update_counselor(counselor, data):
        
        data.pop("user", None)
        data.pop("school", None)
        data.pop("id", None)

        for attr, value in data.items():
            setattr(counselor, attr, value)

        counselor.save()
        return counselor

    @staticmethod
    @transaction.atomic
    def delete_counselor(counselor):

        user = counselor.user
        counselor.delete()
        user.delete()

    @staticmethod
    def reset_password(counselor, new_password):

        user = counselor.user
        user.set_password(new_password)
        user.save()