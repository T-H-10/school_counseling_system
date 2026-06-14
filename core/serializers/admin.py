from rest_framework import serializers

from core.models import School, ClassLevel, SchoolYear, Counselor


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
