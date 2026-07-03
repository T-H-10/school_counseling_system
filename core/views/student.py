from django.db.models import Prefetch
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.filters import StudentFilter
from core.models import SchoolYear, Student, StudentEnrollment
from core.permissions import IsCounselor
from core.serializers import StudentSerializer
from core.services.student_import_export_service import (
    ExcelImportError,
    StudentImportExportService,
)
from core.services.student_report_service import StudentReportService
from core.services.student_service import StudentService
from core.services.student_timeline_service import StudentTimelineService

from .base import BaseSchoolViewSet


class StudentViewSet(BaseSchoolViewSet):
    permission_classes = [IsCounselor]
    model = Student
    serializer_class = StudentSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter

    search_fields = ["full_name", "id_number"]
    ordering_fields = ["full_name", "id_number", "created_at"]
    ordering = ["full_name"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "enrollments",
                    queryset=StudentEnrollment.objects.select_related("class_level", "school_year"),
                ),
                "events",
            )
            .distinct()
        )

    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        student = self.get_object()
        data = StudentTimelineService.get_timeline(student)
        return Response({"student_id": student.id, "timeline": data})

    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        student = self.get_object()

        school_year = None
        year_id = request.query_params.get("year")
        if year_id:
            try:
                school_year = SchoolYear.objects.get(pk=year_id)
            except (SchoolYear.DoesNotExist, ValueError):
                raise ValidationError({"year": ["שנת לימודים לא נמצאה"]})

        data = StudentReportService.get_report(request.user, student, school_year=school_year)
        return Response(data)

    @action(
        detail=False,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser],
    )
    def import_students(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "לא נשלח קובץ"}, status=400)

        try:
            result = StudentImportExportService.import_students(request.user, file)
        except ExcelImportError as e:
            return Response({"error": str(e)}, status=400)

        return Response(result)

    @action(detail=False, methods=["get"], url_path="export")
    def export_students(self, request):
        content = StudentImportExportService.export_students(self.get_queryset())

        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="students.xlsx"'
        return response

    def perform_create(self, serializer):
        student = StudentService.create_student(self.request.user, serializer.validated_data)
        serializer.instance = student

    def perform_update(self, serializer):
        student = StudentService.update_student(
            self.request.user, self.get_object(), serializer.validated_data
        )
        serializer.instance = student

    def perform_destroy(self, instance):
        StudentService.delete_student(self.request.user, instance)
