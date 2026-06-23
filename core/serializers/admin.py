from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import ClassLevel, Counselor, School, SchoolYear


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        return token


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
        read_only_fields = ["created_at"]


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = "__all__"


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = "__all__"
        # The unique_active_school_year partial DB constraint is enforced
        # atomically by SchoolYearService.activate_year(). DRF 3.17+ auto-
        # generates a field-level UniqueValidator from it which would reject
        # valid activation requests before the service even runs — suppress it.
        extra_kwargs = {"is_active": {"validators": []}}


class CounselorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Counselor
        fields = ["id", "username", "password", "full_name", "school", "created_at"]
        read_only_fields = ["created_at"]
