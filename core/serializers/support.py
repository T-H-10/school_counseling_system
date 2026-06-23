from rest_framework import serializers

from core.models import SupportRequest


class SupportRequestSerializer(serializers.ModelSerializer):
    counselor_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = SupportRequest
        fields = [
            "id",
            "subject",
            "message",
            "status",
            "counselor_name",
            "school_name",
            "created_at",
        ]
        read_only_fields = ["status", "counselor_name", "school_name", "created_at"]

    def get_counselor_name(self, obj):
        return obj.counselor.full_name if obj.counselor else None

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None
