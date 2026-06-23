from django_filters.rest_framework import DjangoFilterBackend

from core.models import StudentEvent
from core.permissions import IsCounselor
from core.serializers import StudentEventSerializer
from core.services.student_event_service import StudentEventService

from .base import BaseSchoolViewSet


class StudentEventViewSet(BaseSchoolViewSet):
    permission_classes = [IsCounselor]
    model = StudentEvent
    serializer_class = StudentEventSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student"]

    def perform_create(self, serializer):
        event = StudentEventService.create_event(self.request.user, serializer.validated_data)
        serializer.instance = event

    def perform_update(self, serializer):
        event = StudentEventService.update_event(
            self.request.user, self.get_object(), serializer.validated_data
        )
        serializer.instance = event

    def perform_destroy(self, instance):
        StudentEventService.delete_event(self.request.user, instance)
