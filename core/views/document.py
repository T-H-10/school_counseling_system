import mimetypes
import os
from urllib.parse import quote

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from django.http import FileResponse

from core.models import Document
from core.permissions import DocumentAccessPolicy
from core.serializers import DocumentSerializer
from core.services.document_service import DocumentService

from .base import BaseSchoolViewSet


class DocumentViewSet(BaseSchoolViewSet):
    model = Document
    serializer_class = DocumentSerializer
    permission_classes = [DocumentAccessPolicy]
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'class_level', 'class_number', 'student']

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related('school', 'counselor', 'class_level', 'student')
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        doc = DocumentService.create_document(
            self.request.user,
            serializer.validated_data,
        )
        serializer.instance = doc

    def perform_update(self, serializer):
        doc = DocumentService.update_document(
            self.request.user,
            self.get_object(),
            serializer.validated_data,
        )
        serializer.instance = doc

    def perform_destroy(self, instance):
        DocumentService.delete_document(self.request.user, instance)

    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """Serve the file inline (authenticated, school-scoped). Used for "צפייה"."""
        doc = self.get_object()
        mime, _ = mimetypes.guess_type(doc.file.name)
        mime = mime or 'application/octet-stream'
        response = FileResponse(doc.file.open('rb'), content_type=mime)
        response['Content-Disposition'] = 'inline'
        return response

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Force-download the file (authenticated, school-scoped). Used for "הורדה"."""
        doc = self.get_object()
        ext = os.path.splitext(doc.file.name)[1]
        filename = f'{doc.title}{ext}'
        encoded = quote(filename, safe='')
        response = FileResponse(doc.file.open('rb'))
        response['Content-Disposition'] = (
            f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded}"
        )
        return response
