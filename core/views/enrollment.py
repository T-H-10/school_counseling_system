from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import SchoolYear, StudentEnrollment
from core.permissions import IsCounselor
from core.serializers import StudentEnrollmentSerializer
from core.services.student_enrollment_service import StudentEnrollmentService

from .base import BaseSchoolViewSet


class StudentEnrollmentViewSet(BaseSchoolViewSet):
    permission_classes = [IsCounselor]
    model = StudentEnrollment
    serializer_class = StudentEnrollmentSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student"]

    def perform_create(self, serializer):
        enrollment = StudentEnrollmentService.create_enrollment(
            self.request.user, serializer.validated_data
        )
        serializer.instance = enrollment

    def perform_update(self, serializer):
        enrollment = StudentEnrollmentService.update_enrollment(
            self.request.user, self.get_object(), serializer.validated_data
        )
        serializer.instance = enrollment

    def perform_destroy(self, instance):
        StudentEnrollmentService.delete_enrollment(self.request.user, instance)

    @action(detail=False, methods=["get"], url_path="classes")
    def classes(self, request):
        data = StudentEnrollmentService.get_classes(request.user)
        return Response(data)

    @action(detail=False, methods=["post"], url_path="set-class-teacher")
    def set_class_teacher(self, request):
        required = ["school_year", "class_level", "class_number"]
        missing = [f for f in required if request.data.get(f) is None]
        if missing:
            return Response({"error": f"שדות חסרים: {', '.join(missing)}"}, status=400)
        updated = StudentEnrollmentService.set_class_teacher(request.user, request.data)
        return Response({"updated": updated})

    @action(detail=False, methods=["post"], url_path="promote")
    def promote(self, request):
        from_year = request.data.get("from_year")
        to_year = request.data.get("to_year")
        if not from_year or not to_year:
            return Response({"error": "נדרשים from_year ו-to_year"}, status=400)
        try:
            result = StudentEnrollmentService.promote_students(request.user, request.data)
        except SchoolYear.DoesNotExist:
            return Response({"error": "שנת לימודים לא נמצאה"}, status=400)
        return Response(result)
