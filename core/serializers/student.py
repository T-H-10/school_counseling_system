from rest_framework import serializers

from core.models import ClassLevel, SchoolYear, Student, StudentEnrollment, StudentEvent
from core.validators import validate_id_number, validate_name, validate_phone


class StudentSerializer(serializers.ModelSerializer):
    current_class_level = serializers.SerializerMethodField()
    current_class_number = serializers.SerializerMethodField()
    current_teacher = serializers.SerializerMethodField()
    last_event_date = serializers.SerializerMethodField()
    is_graduated = serializers.SerializerMethodField()
    graduation_year = serializers.SerializerMethodField()

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
        # Uses the prefetch cache — must not call .filter() on the related manager.
        if not hasattr(obj, "_cached_enrollment"):
            candidates = [
                e for e in obj.enrollments.all()
                if e.class_level_id is not None and e.school_year.is_active
            ]
            obj._cached_enrollment = candidates[0] if candidates else None
        return obj._cached_enrollment

    def _get_last_enrollment(self, obj):
        # Uses the prefetch cache — must not call .filter() on the related manager.
        if not hasattr(obj, "_cached_last_enrollment"):
            candidates = sorted(
                [e for e in obj.enrollments.all() if e.class_level_id is not None],
                key=lambda e: (e.school_year.name, e.created_at),
                reverse=True,
            )
            obj._cached_last_enrollment = candidates[0] if candidates else None
        return obj._cached_last_enrollment

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
        dates = [e.date for e in obj.events.all()]
        return max(dates) if dates else None

    def get_is_graduated(self, obj):
        if self._get_current_enrollment(obj):
            return False
        last = self._get_last_enrollment(obj)
        return last is not None and last.class_level is not None and last.class_level.name == "ח"

    def get_graduation_year(self, obj):
        if self._get_current_enrollment(obj):
            return None
        last = self._get_last_enrollment(obj)
        if last and last.class_level and last.class_level.name == "ח":
            return last.school_year.name
        return None

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
            for field in ["school_year", "class_level", "class_number"]:
                if data.get(field) is None:
                    errors[field] = ["שדה זה הוא חובה"]
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
            "parents_status",
            "notes",
            "school",
            "created_at",
            "current_class_level",
            "current_class_number",
            "current_teacher",
            "last_event_date",
            "is_graduated",
            "graduation_year",
            "school_year",
            "class_level",
            "class_number",
        ]
        read_only_fields = [
            "school",
            "created_at",
            "current_class_level",
            "current_class_number",
            "current_teacher",
            "last_event_date",
            "is_graduated",
            "graduation_year",
        ]


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())
    class_level = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(), required=False, allow_null=True
    )
    school_year_name = serializers.CharField(source="school_year.name", read_only=True)
    class_level_name = serializers.CharField(source="class_level.name", read_only=True, allow_null=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "student",
            "school_year",
            "school_year_name",
            "class_level",
            "class_level_name",
            "class_number",
            "teacher_name",
            "school",
            "created_at",
        ]
        read_only_fields = ["school", "created_at", "school_year_name", "class_level_name"]

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
            "created_at",
        ]
        read_only_fields = ["counselor", "school", "created_at"]

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        student = data.get("student")

        if student and student.school != user.counselor.school:
            raise serializers.ValidationError("Student must belong to your school")

        return data
