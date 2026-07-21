from django.core.management.base import BaseCommand

from core.services.backup_service import BackupService


class Command(BaseCommand):
    help = "Create a portable backup archive (DB + media) with a compatibility manifest."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=None,
            help="Directory to write the archive into (default: BACKUP_DIR, or ./backups).",
        )

    def handle(self, *args, **options):
        archive_path = BackupService.create_backup(output_dir=options["output"])
        self.stdout.write(self.style.SUCCESS(f"גיבוי נוצר בהצלחה: {archive_path}"))
