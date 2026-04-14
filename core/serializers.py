from rest_framework import serializers
from core.models import Student
from core.validators import validate_phone, validate_id_number, validate_name


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
        