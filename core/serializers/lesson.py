from django.core.validators import URLValidator
from rest_framework import serializers

from core.models import ClassLevel, LessonClassAssignment, LessonPlan, SchoolYear


class LessonClassAssignmentSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    lesson = serializers.PrimaryKeyRelatedField(queryset=LessonPlan.objects.all())
    class_level = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all())
    class_level_name = serializers.CharField(source="class_level.name", read_only=True)

    class Meta:
        model = LessonClassAssignment
        fields = [
            "id",
            "lesson",
            "school",
            "class_level",
            "class_level_name",
            "class_number",
            "status",
            "planned_date",
            "completed_date",
            "summary",
            "created_at",
        ]
        read_only_fields = ["school", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Scope the lesson choices to the requester's school so a cross-school
        # lesson id fails validation (400) instead of reaching the service.
        request = self.context.get("request")
        if request and hasattr(request.user, "counselor"):
            self.fields["lesson"].queryset = LessonPlan.objects.filter(
                school=request.user.counselor.school
            )


class LessonPlanSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    counselor = serializers.PrimaryKeyRelatedField(read_only=True)

    # http/https only — the URL is rendered as a clickable link in the client.
    presentation_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[URLValidator(schemes=["http", "https"])],
    )

    school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())
    assignments = LessonClassAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = LessonPlan
        fields = [
            "id",
            "school",
            "counselor",
            "school_year",
            "title",
            "description",
            "presentation_url",
            "assignments",
            "created_at",
        ]
        read_only_fields = ["school", "counselor", "created_at"]
