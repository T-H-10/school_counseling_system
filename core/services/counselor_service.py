from core.models import Counselor
from core.services.base import apply_fields
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError


def _check_password_strength(password, user=None, field="password"):
    """Run AUTH_PASSWORD_VALIDATORS; surface failures as a DRF 400, not a 500."""
    try:
        validate_password(password or "", user)
    except DjangoValidationError as e:
        raise ValidationError({field: e.messages})


class CounselorService:
    @staticmethod
    @transaction.atomic
    def create_counselor(data):

        if User.objects.filter(username=data["username"]).exists():
            raise ValidationError({"username": "שם משתמש כבר קיים"})

        user_data = {k: v for k, v in data.items() if k in ["username", "password"]}

        counselor_data = {k: v for k, v in data.items() if k not in ["username", "password", "id"]}

        _check_password_strength(user_data.get("password"))

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
        _check_password_strength(new_password, user, field="new_password")
        user.set_password(new_password)
        user.save()
