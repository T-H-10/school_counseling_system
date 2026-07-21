from django.core.management.base import BaseCommand, CommandError

from core.services.backup_service import BackupIncompatibleError, BackupService


class Command(BaseCommand):
    help = "Restore the database + media from a backup archive created by backup_data."

    def add_arguments(self, parser):
        parser.add_argument("input", help="Path to the backup .zip archive to restore.")

    def handle(self, *args, **options):
        archive_path = options["input"]
        try:
            result = BackupService.restore_backup(archive_path)
        except BackupIncompatibleError as exc:
            raise CommandError(str(exc))

        for warning in result["warnings"]:
            self.stdout.write(self.style.WARNING(warning))
        self.stdout.write(self.style.SUCCESS(f"השחזור הושלם בהצלחה מתוך: {archive_path}"))
