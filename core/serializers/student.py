from rest_framework import serializers

from core.models import ClassLevel, SchoolYear, Student, StudentEnrollment, StudentEvent
from core.validators import validate_phone, validate_id_number, validate_name


class StudentSerializer(serializers.ModelSerializer):

    current_class_level = serializers.SerializerMethodField()
    current_class_number = serializers.SerializerMethodField()
    current_teacher = serializers.SerializerMethodField()
    last_event_date = serializers.SerializerMethodField()

    # Write-only enrollment fields — required on creation, ignored on update
    school_year = serializers.PrimaryKeyRelatedField(
        queryset=SchoolYear.objects.all(),
        write_only=True,
        required=False,
    )
    class_level = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        write_only=True,
        required=False,
    )
    class_number = serializers.IntegerField(
        write_only=True,
        required=False,
        min_value=1,
    )

    def _get_current_enrollment(self, obj):
        if not hasattr(obj, '_cached_enrollment'):
            obj._cached_enrollment = (
                obj.enrollments
                   .select_related('class_level', 'school_year')
                   .filter(class_level__isnull=False)
                   .order_by('-school_year__is_active', '-created_at')
                   .first()
            )
        return obj._cached_enrollment

    def get_current_class_level(self, obj):
        enrollment = self._get_current_enrollment(obj)
        return enrollment.class_level.name if enrollment else None

    def get_current_class_number(self, obj):
        enrollment = self._get_current_enrollment(obj)
        return enrollment.class_number if enrollment else None

    def get_current_teacher(self, obj):
        enrollment = self._get_current_enrollment(obj)
        return enrollment.teacher_name if enrollment else None

    def get_last_event_date(self, obj):
        return obj.events.order_by('-date').values_list('date', flat=True).first()

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

    def validate(self, data):
        if not self.instance:  # creation — enrollment fields are mandatory
            errors = {}
            for field in ['school_year', 'class_level', 'class_number']:
                if data.get(field) is None:
                    errors[field] = ['שדה זה הוא חובה']
            if errors:
                raise serializers.ValidationError(errors)
        return data

    class Meta:
        model = Student
        fields = [
            "id",
            "full_name",
            "id_number",
            "address",
            "mother_name",
            "mother_phone",
            "father_name",
            "father_phone",
            "school",
            "created_at",
            "current_class_level",
            "current_class_number",
            "current_teacher",
            "last_event_date",
            "school_year",
            "class_level",
            "class_number",
        ]
        read_only_fields = ["school", "created_at", "current_class_level", "current_class_number", "current_teacher", "last_event_date"]


class StudentEnrollmentSerializer(serializers.ModelSerializer):

    school = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())
    class_level = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            "id", "student", "school_year", "class_level", "class_number",
            "teacher_name", "school", "created_at"
        ]
        read_only_fields = ["school", "created_at"]

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        student = data.get("student")

        if student and student.school != user.counselor.school:
            raise serializers.ValidationError("Student must belong to your school")

        return data


class StudentEventSerializer(serializers.ModelSerializer):

    counselor = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = StudentEvent
        fields = [
            "id",
            "student",
            "counselor",
            "event_type",
            "title",
            "agenda",
            "description",
            "date",
            "end_date",
            "status",
            "school",
            "created_at"
        ]
        read_only_fields = ["counselor", "school", "created_at"]

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        student = data.get("student")

        if student and student.school != user.counselor.school:
            raise serializers.ValidationError("Student must belong to your school")

        return data
