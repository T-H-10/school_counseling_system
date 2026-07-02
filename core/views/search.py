from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCounselor
from core.services.global_search_service import GlobalSearchService


class GlobalSearchView(APIView):
    permission_classes = [IsCounselor]

    def get(self, request):
        query = request.query_params.get("q", "")
        data = GlobalSearchService.search(request.user, query)
        return Response(data)
