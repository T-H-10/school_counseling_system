from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCounselor
from core.services.dashboard_service import DashboardService


class DashboardView(APIView):
    permission_classes = [IsCounselor]

    def get(self, request):
        data = DashboardService.get_dashboard(request.user)
        return Response(data)
