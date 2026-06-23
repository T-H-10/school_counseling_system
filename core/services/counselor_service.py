from core.models import Counselor
from core.services.base import apply_fields
from django.contrib.auth.models import User
from django.db import transaction


class CounselorService:
    @staticmethod
    @transaction.atomic
    def create_counselor(data):

        if User.objects.filter(username=data["username"]).exists():
            raise ValueError("Username already exists")

        user_data = {k: v for k, v in data.items() if k in ["username", "password"]}

        counselor_data = {k: v for k, v in data.items() if k not in ["username", "password", "id"]}

        user = User.objects.create_user(
            username=user_data["username"], password=user_data["password"]
        )

        return Counselor.objects.create(user=user, **counselor_data)

    @staticmethod
    def update_counselor(counselor, data):
        return apply_fields(counselor, data, exclude=["user", "school", "id"])

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
