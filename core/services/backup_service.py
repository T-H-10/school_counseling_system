"""Backup & restore: snapshot the database + media into one portable archive.

The archive is DB-engine agnostic (JSON fixtures via ``dumpdata``/``loaddata``)
so the same backup produced against SQLite (desktop/hybrid) can be restored
into PostgreSQL (cloud) and vice versa — no raw copy of the database file. A
``manifest.json`` travels alongside the data so ``restore_backup`` can detect
an incompatible schema before touching anything.
"""

import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core import management
from django.db import connection
from django.db.migrations.loader import MigrationLoader

MANIFEST_NAME = "manifest.json"
DATA_NAME = "data.json"
MEDIA_PREFIX = "media/"

# Excluded from the data dump: derived/ephemeral tables that either
# regenerate themselves (the scheduler's job store, content types/permissions
# rebuilt by `migrate`) or would carry stale security state across a restore
# (sessions, outstanding/blacklisted JWTs).
DUMP_EXCLUDES = [
    "contenttypes",
    "auth.permission",
    "admin.logentry",
    "sessions.session",
    "token_blacklist.outstandingtoken",
    "token_blacklist.blacklistedtoken",
    "django_apscheduler.djangojob",
    "django_apscheduler.djangojobexecution",
]


class BackupIncompatibleError(Exception):
    """Raised when an archive's schema is newer than the current codebase understands."""


class BackupService:
    @staticmethod
    def _schema_version():
        """``{app_label: [leaf migration names]}`` — a fingerprint of which
        migrations the *current codebase* knows about, used to detect a
        backup produced by a newer/incompatible version of the app.
        """
        loader = MigrationLoader(connection)
        versions = {}
        for app_label, migration_name in loader.graph.leaf_nodes():
            versions.setdefault(app_label, []).append(migration_name)
        return versions

    @staticmethod
    def build_manifest():
        return {
            "app_version": settings.APP_VERSION,
            "schema_version": BackupService._schema_version(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "deployment_mode": settings.DEPLOYMENT_MODE,
        }

    @staticmethod
    def _default_dir():
        return Path(settings.BACKUP_DIR) if settings.BACKUP_DIR else (settings.BASE_DIR / "backups")

    @staticmethod
    def create_backup(output_dir=None):
        """Write a new backup archive and return its path.

        Safe to run live: ``dumpdata`` takes one read pass over the database
        (no locks held for the duration), and the archive is assembled at a
        temp path then moved into place, so a reader never sees a partial
        file. Idempotent in the sense that matters for a backup command —
        each run is a fresh, independent, timestamped snapshot with no shared
        state to corrupt on repeat runs.
        """
        target_dir = Path(output_dir) if output_dir else BackupService._default_dir()
        target_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        archive_path = target_dir / f"backup_{timestamp}.zip"
        tmp_path = archive_path.with_suffix(".zip.tmp")

        fd, dump_tmp_name = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with open(dump_tmp_name, "w", encoding="utf-8") as dump_file:
                management.call_command(
                    "dumpdata",
                    exclude=DUMP_EXCLUDES,
                    indent=2,
                    stdout=dump_file,
                )

            manifest = BackupService.build_manifest()

            with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, indent=2))
                archive.write(dump_tmp_name, DATA_NAME)
                media_root = Path(settings.MEDIA_ROOT)
                if media_root.exists():
                    for file_path in media_root.rglob("*"):
                        if file_path.is_file():
                            archive.write(file_path, MEDIA_PREFIX + str(file_path.relative_to(media_root)))
        finally:
            os.unlink(dump_tmp_name)

        tmp_path.replace(archive_path)
        return archive_path

    @staticmethod
    def list_backups(directory=None):
        target_dir = Path(directory) if directory else BackupService._default_dir()
        if not target_dir.exists():
            return []
        entries = []
        for path in sorted(target_dir.glob("backup_*.zip"), reverse=True):
            stat = path.stat()
            entries.append(
                {
                    "filename": path.name,
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                }
            )
        return entries

    @staticmethod
    def resolve_backup_path(filename, directory=None):
        """Look up an existing backup by name inside the backups directory.

        Strips any directory components from ``filename`` first so a caller
        can never escape the backups directory via ``../`` path traversal.
        """
        target_dir = Path(directory) if directory else BackupService._default_dir()
        candidate = target_dir / Path(filename).name
        return candidate if candidate.exists() else None

    @staticmethod
    def save_uploaded_backup(uploaded_file, directory=None):
        target_dir = Path(directory) if directory else BackupService._default_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        dest = target_dir / f"uploaded_{timestamp}.zip"
        with open(dest, "wb") as out:
            for chunk in uploaded_file.chunks():
                out.write(chunk)
        return dest

    @staticmethod
    def read_manifest(archive_path):
        with zipfile.ZipFile(archive_path) as archive:
            return json.loads(archive.read(MANIFEST_NAME))

    @staticmethod
    def check_compatibility(manifest):
        """Compare the archive's recorded schema against the current
        codebase's migration graph.

        Returns a list of Hebrew warning strings for anything that's merely
        outdated (safe to proceed — ``migrate`` brings it forward). Raises
        ``BackupIncompatibleError`` if the archive references a migration the
        current codebase has never heard of — it was produced by a newer
        version, and loading its data could silently misplace fields the
        current schema no longer expects.
        """
        warnings = []
        loader = MigrationLoader(connection)
        current = BackupService._schema_version()
        backup_schema = manifest.get("schema_version", {})

        for app_label, leaf_names in backup_schema.items():
            known = {name for (label, name) in loader.graph.nodes if label == app_label}
            for leaf_name in leaf_names:
                if leaf_name not in known:
                    raise BackupIncompatibleError(
                        "הגיבוי נוצר על ידי גרסה חדשה יותר של המערכת "
                        f"(מיגרציה לא מוכרת: {app_label}.{leaf_name}). לא ניתן לשחזר."
                    )
            if set(current.get(app_label, [])) != set(leaf_names):
                warnings.append(
                    f"הגיבוי מבוסס על סכמה ישנה יותר עבור '{app_label}' — "
                    "השחזור יעדכן את הסכמה לפני טעינת הנתונים."
                )

        backup_app_version = manifest.get("app_version")
        if backup_app_version and backup_app_version != settings.APP_VERSION:
            warnings.append(
                f"גרסת האפליקציה בגיבוי ({backup_app_version}) שונה מהגרסה "
                f"הנוכחית ({settings.APP_VERSION})."
            )
        return warnings

    @staticmethod
    def restore_backup(archive_path):
        """Restore an archive: validate the manifest, bring the schema up to
        date, load the data fixture, and copy media files into MEDIA_ROOT.

        Returns ``{"manifest": ..., "warnings": [...]}``. Raises
        ``BackupIncompatibleError`` without touching anything if the archive
        is from a newer, incompatible schema.
        """
        manifest = BackupService.read_manifest(archive_path)
        warnings = BackupService.check_compatibility(manifest)

        management.call_command("migrate", interactive=False, verbosity=0)

        with zipfile.ZipFile(archive_path) as archive:
            data_bytes = archive.read(DATA_NAME)
            media_root = Path(settings.MEDIA_ROOT)
            media_root.mkdir(parents=True, exist_ok=True)
            for name in archive.namelist():
                if name.startswith(MEDIA_PREFIX) and not name.endswith("/"):
                    relative = name[len(MEDIA_PREFIX) :]
                    dest = media_root / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(archive.read(name))

        fd, tmp_data_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, "wb") as tmp_file:
                tmp_file.write(data_bytes)
            management.call_command("loaddata", tmp_data_path, format="json", verbosity=0)
        finally:
            os.unlink(tmp_data_path)

        return {"manifest": manifest, "warnings": warnings}
