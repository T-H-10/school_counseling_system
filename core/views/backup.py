import zipfile

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.services.backup_service import BackupIncompatibleError, BackupService


class BackupViewSet(ViewSet):
    """Admin-only backup/restore control surface.

    Registered only when ``settings.IS_LOCAL_MODE`` (see ``core/urls.py``) —
    cloud relies on the managed provider's own backups (see
    ``docs/completion-plan.md`` Step C2) plus the same ``backup_data`` /
    ``restore_data`` management commands, which remain available in every
    deployment mode regardless of this API.
    """

    permission_classes = [IsAdminUser]

    def list(self, request):
        return Response(BackupService.list_backups())

    def create(self, request):
        archive_path = BackupService.create_backup()
        manifest = BackupService.read_manifest(archive_path)
        return Response(
            {"filename": archive_path.name, "manifest": manifest}, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"])
    def restore(self, request):
        filename = request.data.get("filename")
        upload = request.FILES.get("file")
        if not filename and not upload:
            return Response({"detail": "יש לציין קובץ גיבוי לשחזור"}, status=status.HTTP_400_BAD_REQUEST)

        if upload:
            if not zipfile.is_zipfile(upload):
                return Response({"detail": "קובץ הגיבוי אינו תקין"}, status=status.HTTP_400_BAD_REQUEST)
            archive_path = BackupService.save_uploaded_backup(upload)
        else:
            archive_path = BackupService.resolve_backup_path(filename)
            if archive_path is None:
                return Response({"detail": "קובץ הגיבוי לא נמצא"}, status=status.HTTP_404_NOT_FOUND)

        try:
            result = BackupService.restore_backup(archive_path)
        except BackupIncompatibleError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(result)
