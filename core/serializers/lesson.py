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


class LessonPlanSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    counselor = serializers.PrimaryKeyRelatedField(read_only=True)

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
