from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.services.lesson_plan_service import LessonPlanService
from core.services.lesson_class_assignment_service import LessonClassAssignmentService
from core.models import LessonPlan, LessonClassAssignment
from core.serializers import LessonPlanSerializer, LessonClassAssignmentSerializer
from core.permissions import IsCounselor

from .base import BaseSchoolViewSet


class LessonPlanViewSet(BaseSchoolViewSet):
    permission_classes = [IsCounselor]
    model = LessonPlan
    serializer_class = LessonPlanSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("assignments__class_level")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        lesson = LessonPlanService.create_lesson(
            self.request.user, serializer.validated_data
        )
        serializer.instance = lesson

    def perform_update(self, serializer):
        lesson = LessonPlanService.update_lesson(
            self.request.user, self.get_object(), serializer.validated_data
        )
        serializer.instance = lesson

    def perform_destroy(self, instance):
        LessonPlanService.delete_lesson(self.request.user, instance)

    @action(detail=False, methods=["get"])
    def calendar(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        data = LessonPlanService.get_calendar(request.user, start, end)
        return Response(data)


class LessonClassAssignmentViewSet(BaseSchoolViewSet):
    permission_classes = [IsCounselor]
    model = LessonClassAssignment
    serializer_class = LessonClassAssignmentSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lesson"]

    def perform_create(self, serializer):
        assignment = LessonClassAssignmentService.assign_class(
            self.request.user, serializer.validated_data
        )
        serializer.instance = assignment

    def perform_update(self, serializer):
        assignment = LessonClassAssignmentService.update_assignment(
            self.request.user, self.get_object(), serializer.validated_data
        )
        serializer.instance = assignment

    def perform_destroy(self, instance):
        LessonClassAssignmentService.delete_assignment(self.request.user, instance)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        assignment = self.get_object()
        assignment = LessonClassAssignmentService.complete_assignment(
            request.user, assignment, request.data
        )
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
