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


class CounselorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Counselor
        fields = ["id", "username", "password", "full_name", "school", "created_at"]
        read_only_fields = ["created_at"]
