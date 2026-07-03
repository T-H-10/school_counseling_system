"""Phase-4 hardening: password validation, generic 500s, import signature,
and presentation_url scheme restriction."""

import io

import pytest

from core.services.student_import_export_service import (
    ExcelImportError,
    StudentImportExportService,
)
from core.tests import factories
from core.tests.factories import DEFAULT_PASSWORD

pytestmark = pytest.mark.django_db


# --- counselor password validation ------------------------------------------


def test_reset_password_rejects_weak_password(admin_client, counselor_a):
    resp = admin_client.post(f"/counselors/{counselor_a.id}/reset_password/", {"new_password": "123"})
    assert resp.status_code == 400
    assert "new_password" in resp.data


def test_reset_password_missing_field_returns_400_not_500(admin_client, counselor_a):
    resp = admin_client.post(f"/counselors/{counselor_a.id}/reset_password/", {})
    assert resp.status_code == 400


def test_reset_password_strong_password_works(admin_client, api, counselor_a):
    resp = admin_client.post(
        f"/counselors/{counselor_a.id}/reset_password/", {"new_password": "Str0ng!Passw0rd"}
    )
    assert resp.status_code == 200
    login = api.post(
        "/token/", {"username": counselor_a.user.username, "password": "Str0ng!Passw0rd"}
    )
    assert login.status_code == 200


def test_create_counselor_rejects_weak_password(admin_client, school_a):
    resp = admin_client.post(
        "/counselors/",
        {"username": "newuser1", "password": "123", "full_name": "יועצת חדשה", "school": school_a.id},
    )
    assert resp.status_code == 400
    assert "password" in resp.data


def test_create_counselor_duplicate_username_returns_400_not_500(admin_client, counselor_a, school_a):
    resp = admin_client.post(
        "/counselors/",
        {
            "username": counselor_a.user.username,
            "password": DEFAULT_PASSWORD,
            "full_name": "כפולה",
            "school": school_a.id,
        },
    )
    assert resp.status_code == 400
    assert "username" in resp.data


# --- generic 500 handler ------------------------------------------------------


def test_unhandled_exception_returns_uniform_json(client_a, monkeypatch):
    from core.services.dashboard_service import DashboardService

    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail: table core_student")

    monkeypatch.setattr(DashboardService, "get_dashboard", boom)
    resp = client_a.get("/dashboard/")
    assert resp.status_code == 500
    assert resp.data == {"error": "אירעה שגיאה פנימית"}


# --- import magic-byte pre-check ---------------------------------------------


def test_import_rejects_non_zip_file(counselor_a):
    fake_xlsx = io.BytesIO(b"MZ\x90\x00 this is not a zip")
    with pytest.raises(ExcelImportError):
        StudentImportExportService.import_students(counselor_a.user, fake_xlsx)


# --- presentation_url scheme restriction --------------------------------------


def test_lesson_rejects_javascript_url(client_a, active_year):
    resp = client_a.post(
        "/lessons/",
        {
            "title": "שיעור",
            "school_year": active_year.id,
            "presentation_url": "javascript:alert(1)",
        },
    )
    assert resp.status_code == 400
    assert "presentation_url" in resp.data


def test_lesson_accepts_https_url(client_a, active_year):
    resp = client_a.post(
        "/lessons/",
        {
            "title": "שיעור",
            "school_year": active_year.id,
            "presentation_url": "https://drive.google.com/file/d/abc",
        },
    )
    assert resp.status_code == 201
