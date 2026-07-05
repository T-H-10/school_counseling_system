from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from core.models import ClassLevel, Counselor, School, SchoolYear
from core.serializers import (
    ArchiveEntrySerializer,
    ClassLevelSerializer,
    CounselorSerializer,
    SchoolSerializer,
    SchoolYearSerializer,
)
from core.services.archive_service import ENTITY_MODELS, ArchiveIntegrityError, ArchiveService
from core.services.class_level_service import ClassLevelService
from core.services.counselor_service import CounselorService
from core.services.school_service import SchoolService
from core.services.school_year_service import SchoolYearService


class SchoolViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    # Admin school management has no pagination UI and expects the full list
    # (a district's school count is bounded, unlike Students) — global
    # PageNumberPagination would silently hide schools past page_size=20.
    pagination_class = None

    def perform_create(self, serializer):
        school = SchoolService.create_school(serializer.validated_data)
        serializer.instance = school

    def perform_update(self, serializer):
        school = SchoolService.update_school(self.get_object(), serializer.validated_data)
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
        level = ClassLevelService.update_class_level(self.get_object(), serializer.validated_data)
        serializer.instance = level

    def perform_destroy(self, instance):
        ClassLevelService.delete_class_level(instance)


class SchoolYearViewSet(ModelViewSet):
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        year = SchoolYearService.create_school_year(serializer.validated_data)
        serializer.instance = year

    def perform_update(self, serializer):
        year = SchoolYearService.update_school_year(self.get_object(), serializer.validated_data)
        serializer.instance = year

    def perform_destroy(self, instance):
        SchoolYearService.delete_school_year(instance)


class CounselorViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Counselor.objects.all()
    serializer_class = CounselorSerializer
    # Same rationale as SchoolViewSet — the admin counselors table has no
    # pagination UI and expects the full list.
    pagination_class = None

    def perform_create(self, serializer):
        counselor = CounselorService.create_counselor(serializer.validated_data)
        serializer.instance = counselor

    def perform_update(self, serializer):
        counselor = CounselorService.update_counselor(self.get_object(), serializer.validated_data)
        serializer.instance = counselor

    def perform_destroy(self, instance):
        CounselorService.delete_counselor(instance)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reset_password(self, request, pk=None):
        counselor = self.get_object()

        CounselorService.reset_password(counselor, request.data.get("new_password", ""))

        return Response({"status": "password updated"})


class AdminArchiveViewSet(GenericViewSet):
    """Admin-only browser for soft-deleted rows across all 5 archivable
    entities. Not a BaseSchoolViewSet subclass: there's no single "caller
    school" to scope to (the caller is an admin, not tied to one school), and
    these rows are invisible to any counselor of the owning school through
    every other viewset anyway (soft-deleted). ``entity_type`` query param
    picks which of the 5 models a given request operates on.
    """

    permission_classes = [IsAdminUser]
    serializer_class = ArchiveEntrySerializer

    def _entity_type(self):
        entity_type = self.request.query_params.get("entity_type")
        if entity_type not in ENTITY_MODELS:
            raise ValidationError({"entity_type": "פרמטר entity_type חסר או לא תקין"})
        return entity_type

    def list(self, request):
        entity_type = self._entity_type()
        qs = ArchiveService.list_archived(
            entity_type,
            school=request.query_params.get("school"),
            deleted_after=request.query_params.get("deleted_after"),
            deleted_before=request.query_params.get("deleted_before"),
        )
        page = self.paginate_queryset(qs)
        rows = page if page is not None else list(qs)
        data = self.get_serializer(ArchiveService.serialize_list(entity_type, rows), many=True).data
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        entity_type = self._entity_type()
        try:
            instance = ArchiveService.restore(entity_type, pk)
        except ObjectDoesNotExist:
            raise NotFound("הרשומה לא נמצאה")
        except ArchiveIntegrityError as exc:
            raise ValidationError({"detail": exc.reason})
        data = self.get_serializer(ArchiveService.serialize_one(entity_type, instance)).data
        return Response(data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        return Response(ArchiveService.counts_by_entity(school=request.query_params.get("school")))
