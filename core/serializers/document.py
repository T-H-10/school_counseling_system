import os

from rest_framework import serializers

from core.models import ClassLevel, Document, Student
from core.models.document import validate_document_category
from core.validators import validate_document_file


class DocumentSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    counselor = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class_level = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        required=False,
        allow_null=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=False,
        allow_null=True,
    )

    file = serializers.FileField(validators=[validate_document_file])

    class_level_name = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    def get_class_level_name(self, obj):
        return obj.class_level.name if obj.class_level else None

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else None

    def get_file_size(self, obj):
        try:
            return obj.file.size
        except Exception:
            return None

    def validate(self, data):
        category = data.get('category', getattr(self.instance, 'category', None))
        student = data.get('student', getattr(self.instance, 'student', None))
        class_level = data.get('class_level', getattr(self.instance, 'class_level', None))

        errors = validate_document_category(category, student, class_level)
        if errors:
            raise serializers.ValidationError(errors)
        return data

    class Meta:
        model = Document
        fields = [
            'id',
            'school',
            'counselor',
            'category',
            'title',
            'description',
            'file',
            'file_name',
            'file_size',
            'class_level',
            'class_level_name',
            'class_number',
            'student',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'school',
            'counselor',
            'created_at',
            'updated_at',
            'class_level_name',
            'file_name',
            'file_size',
        ]
