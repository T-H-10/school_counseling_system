from rest_framework.views import APIView
from rest_framework.response import Response

from core.services.dashboard_service import DashboardService
from core.permissions import IsCounselor


class DashboardView(APIView):
    permission_classes = [IsCounselor]

    def get(self, request):
        data = DashboardService.get_dashboard(request.user)
        return Response(data)
