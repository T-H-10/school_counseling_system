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
    student_name = serializers.SerializerMethodField()
    student_id_number = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    def get_class_level_name(self, obj):
        return obj.class_level.name if obj.class_level else None

    def get_student_name(self, obj):
        return obj.student.full_name if obj.student else None

    def get_student_id_number(self, obj):
        return obj.student.id_number if obj.student else None

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else None

    def get_file_size(self, obj):
        try:
            return obj.file.size
        except Exception:
            return None

    def validate(self, data):
        new_category = data.get('category', getattr(self.instance, 'category', None))

        # When category changes on an update, auto-clear relations that no longer belong.
        # This lets callers send only the new required fields without explicitly nulling
        # the old ones — the single source of truth stays validate_document_category().
        if self.instance and 'category' in data and data['category'] != self.instance.category:
            if new_category != 'student':
                data['student'] = None
            if new_category != 'class':
                data['class_level'] = None
                data['class_number'] = None

        student = data.get('student', getattr(self.instance, 'student', None))
        class_level = data.get('class_level', getattr(self.instance, 'class_level', None))

        errors = validate_document_category(new_category, student, class_level)
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
            'student_name',
            'student_id_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'school',
            'counselor',
            'created_at',
            'updated_at',
            'class_level_name',
            'student_name',
            'student_id_number',
            'file_name',
            'file_size',
        ]
