from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import SupportRequest
from core.permissions import IsCounselor
from core.serializers.support import SupportRequestSerializer
from core.services.support_request_service import SupportRequestService


class SupportRequestViewSet(ModelViewSet):
    serializer_class = SupportRequestSerializer
    http_method_names = ["get", "post", "head", "options"]
    # The admin support page filters client-side via tabs (open/resolved/all)
    # over the whole list, with no pagination UI — global PageNumberPagination
    # would silently hide requests past page_size=20.
    pagination_class = None

    def get_permissions(self):
        if self.action == "create":
            return [IsCounselor()]
        return [IsAdminUser()]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SupportRequest.objects.none()
        user = self.request.user
        if user.is_staff:
            return SupportRequest.objects.select_related("counselor", "school").all()
        if hasattr(user, "counselor"):
            return SupportRequest.objects.filter(school=user.counselor.school)
        return SupportRequest.objects.none()

    def perform_create(self, serializer):
        req = SupportRequestService.create_request(self.request.user, serializer.validated_data)
        serializer.instance = req

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def resolve(self, request, pk=None):
        support_req = self.get_object()
        SupportRequestService.resolve_request(support_req)
        return Response(SupportRequestSerializer(support_req).data)
