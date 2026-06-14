from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.services.school_service import SchoolService
from core.services.class_level_service import ClassLevelService
from core.services.school_year_service import SchoolYearService
from core.services.counselor_service import CounselorService
from core.models import School, ClassLevel, SchoolYear, Counselor
from core.serializers import SchoolSerializer, ClassLevelSerializer, SchoolYearSerializer, CounselorSerializer


class SchoolViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def perform_create(self, serializer):
        school = SchoolService.create_school(serializer.validated_data)
        serializer.instance = school

    def perform_update(self, serializer):
        school = SchoolService.update_school(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = school

    def perform_destroy(self, instance):
        SchoolService.delete_school(instance)


class ClassLevelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ClassLevel.objects.all()
    serializer_class = ClassLevelSerializer

    def perform_create(self, serializer):
        level = ClassLevelService.create_class_level(serializer.validated_data)
        serializer.instance = level

    def perform_update(self, serializer):
        level = ClassLevelService.update_class_level(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = level

    def perform_destroy(self, instance):
        ClassLevelService.delete_class_level(instance)


class SchoolYearViewSet(ModelViewSet):
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        year = SchoolYearService.create_school_year(serializer.validated_data)
        serializer.instance = year

    def perform_update(self, serializer):
        year = SchoolYearService.update_school_year(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = year

    def perform_destroy(self, instance):
        SchoolYearService.delete_school_year(
            instance
            )


class CounselorViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Counselor.objects.all()
    serializer_class = CounselorSerializer

    def perform_create(self, serializer):
        counselor = CounselorService.create_counselor(
            serializer.validated_data
            )
        serializer.instance = counselor

    def perform_update(self, serializer):
        counselor = CounselorService.update_counselor(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = counselor

    def perform_destroy(self, instance):
        CounselorService.delete_counselor(
            instance
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reset_password(self, request, pk=None):
        counselor = self.get_object()

        CounselorService.reset_password(
            counselor,
            request.data["new_password"]
        )

        return Response({"status": "password updated"})
