from rest_framework import serializers
from core.models import School, ClassLevel, SchoolYear, Counselor, Student, StudentEnrollment, ClassSession
from core.validators import validate_phone, validate_id_number, validate_name


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

    class Meta:
        model = Counselor
        fields = ["id", "full_name", "school", "created_at"]
        read_only_fields = ["created_at"]


class StudentSerializer(serializers.ModelSerializer):

    def validate_full_name(self, value):
        validate_name(value)
        return value

    def validate_id_number(self, value):
        validate_id_number(value)
        return value

    def validate_mother_phone(self, value):
        if value:
            validate_phone(value)
        return value

    def validate_father_phone(self, value):
        if value:
            validate_phone(value)
        return value

    class Meta:
        model = Student
        fields = "__all__"
        read_only_fields = ["school", "created_at"]
        

class StudentEnrollmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentEnrollment
        fields = "__all__"
        read_only_fields = ["school", "created_at"]


class ClassSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassSession
        fields = "__all__"
        read_only_fields = ["school", "counselor", "created_at"]






