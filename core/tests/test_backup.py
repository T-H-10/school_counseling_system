"""Backup & restore (Step 5): archive format, manifest compatibility, and the
core round-trip guarantee — a backup taken before data loss can bring it back.
"""

import zipfile

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from core.services.backup_service import BackupIncompatibleError, BackupService
from core.tests import factories
from core.views.backup import BackupViewSet

pytestmark = pytest.mark.django_db


def test_create_backup_writes_manifest_data_and_media(tmp_path, school_a, counselor_a):
    factories.StudentFactory(school=school_a, full_name="גיבוי בדיקה")

    archive_path = BackupService.create_backup(output_dir=tmp_path)

    assert archive_path.exists()
    assert archive_path.parent == tmp_path
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert "manifest.json" in names
        assert "data.json" in names

    manifest = BackupService.read_manifest(archive_path)
    assert manifest["app_version"]
    assert manifest["deployment_mode"] in {"desktop", "cloud", "hybrid"}
    assert "core" in manifest["schema_version"]
    assert manifest["created_at"]


def test_list_backups_returns_newest_first(tmp_path, school_a):
    first = BackupService.create_backup(output_dir=tmp_path)
    second = BackupService.create_backup(output_dir=tmp_path)

    entries = BackupService.list_backups(directory=tmp_path)

    assert [e["filename"] for e in entries] == [second.name, first.name]


def test_list_backups_empty_when_directory_missing(tmp_path):
    missing = tmp_path / "does-not-exist"
    assert BackupService.list_backups(directory=missing) == []


def test_resolve_backup_path_rejects_path_traversal(tmp_path, school_a):
    BackupService.create_backup(output_dir=tmp_path)

    assert BackupService.resolve_backup_path("../../etc/passwd", directory=tmp_path) is None
    assert BackupService.resolve_backup_path("nonexistent.zip", directory=tmp_path) is None


def test_restore_round_trip_recreates_deleted_student(tmp_path, school_a, counselor_a):
    student = factories.StudentFactory(
        school=school_a, full_name="שוחזרת מגיבוי", id_number="123456782"
    )
    student_id = student.id

    archive_path = BackupService.create_backup(output_dir=tmp_path)

    student.delete()  # BaseModel soft-delete
    from core.models import Student

    Student.all_objects.filter(pk=student_id).delete()  # hard-delete to prove restore recreates the row
    assert not Student.all_objects.filter(pk=student_id).exists()

    result = BackupService.restore_backup(archive_path)

    assert result["warnings"] == []
    restored = Student.all_objects.get(pk=student_id)
    assert restored.full_name == "שוחזרת מגיבוי"
    assert restored.id_number == "123456782"
    assert restored.deleted_at is None


def test_restore_refuses_on_unknown_future_migration(tmp_path, school_a):
    archive_path = BackupService.create_backup(output_dir=tmp_path)
    manifest = BackupService.read_manifest(archive_path)
    manifest["schema_version"]["core"] = ["9999_migration_from_the_future"]

    tampered = tmp_path / "tampered.zip"
    with zipfile.ZipFile(archive_path) as src, zipfile.ZipFile(tampered, "w") as dst:
        import json

        for name in src.namelist():
            if name == "manifest.json":
                dst.writestr(name, json.dumps(manifest))
            else:
                dst.writestr(name, src.read(name))

    with pytest.raises(BackupIncompatibleError):
        BackupService.restore_backup(tampered)


def test_restore_warns_on_older_schema(tmp_path, school_a):
    archive_path = BackupService.create_backup(output_dir=tmp_path)
    manifest = BackupService.read_manifest(archive_path)
    manifest["schema_version"]["core"] = ["0001_initial"]

    tampered = tmp_path / "older.zip"
    with zipfile.ZipFile(archive_path) as src, zipfile.ZipFile(tampered, "w") as dst:
        import json

        for name in src.namelist():
            if name == "manifest.json":
                dst.writestr(name, json.dumps(manifest))
            else:
                dst.writestr(name, src.read(name))

    result = BackupService.restore_backup(tampered)
    assert any("core" in w for w in result["warnings"])


# --- API permission gate ----------------------------------------------------


def test_backup_viewset_requires_admin(admin_user, counselor_a):
    factory = APIRequestFactory()

    list_view = BackupViewSet.as_view({"get": "list"})

    request = factory.get("/backup/")
    force_authenticate(request, user=counselor_a.user)
    response = list_view(request)
    assert response.status_code == 403

    request = factory.get("/backup/")
    force_authenticate(request, user=admin_user)
    response = list_view(request)
    assert response.status_code == 200
