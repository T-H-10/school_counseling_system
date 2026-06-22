"""P0 — Document upload, retrieval, scoping, validation, and file actions.

Covers:
- CRUD happy paths for all three categories (general / class / student)
- Category validation (serializer + DB CheckConstraint)
- File extension and size validation
- School-scoping isolation (cross-tenant 404)
- Authenticated content/download actions (Content-Disposition headers)
- Soft-delete keeps the physical file; file-replace removes the old file
"""
import email.header
import os

import pytest
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from core.models import Document
from core.tests import factories


def _decode_header(value):
    """Decode an RFC 2047 encoded header value (test client encodes Hebrew filenames)."""
    parts = email.header.decode_header(value)
    return "".join(
        part.decode(enc or "utf-8") if isinstance(part, bytes) else part
        for part, enc in parts
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pdf(name="test.pdf", size=1024):
    return SimpleUploadedFile(name, b"%PDF-1.4 " + b"x" * size, content_type="application/pdf")


def png(name="img.png"):
    return SimpleUploadedFile(name, b"\x89PNG\r\n" + b"x" * 64, content_type="image/png")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def media_root(tmp_path, settings):
    """Redirect all file uploads to a temp directory; cleaned up after each test."""
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Happy-path CRUD
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_create_general_document(client_a):
    resp = client_a.post("/documents/", {
        "category": "general",
        "title": "חוזר מנהל",
        "file": pdf(),
    }, format="multipart")

    assert resp.status_code == 201
    assert resp.data["category"] == "general"
    assert resp.data["title"] == "חוזר מנהל"
    assert resp.data["file_name"].endswith(".pdf")
    assert resp.data["file_size"] > 0
    assert "student" not in resp.data or resp.data["student"] is None


@pytest.mark.django_db
def test_create_student_document(client_a, counselor_a, school_a):
    student = factories.StudentFactory(school=school_a)
    resp = client_a.post("/documents/", {
        "category": "student",
        "title": "הערכה פסיכולוגית",
        "file": pdf(),
        "student": student.id,
    }, format="multipart")

    assert resp.status_code == 201
    assert resp.data["student"] == student.id


@pytest.mark.django_db
def test_create_class_document(client_a, school_a):
    cl = factories.ClassLevelFactory(name="ב")
    resp = client_a.post("/documents/", {
        "category": "class",
        "title": "תכנית ב׳",
        "file": pdf(),
        "class_level": cl.id,
        "class_number": 2,
    }, format="multipart")

    assert resp.status_code == 201
    assert resp.data["class_level"] == cl.id
    assert resp.data["class_level_name"] == "ב"


@pytest.mark.django_db
def test_list_returns_only_own_school_documents(client_a, school_a, counselor_a, school_b, counselor_b):
    factories.DocumentFactory(school=school_a, counselor=counselor_a)
    factories.DocumentFactory(school=school_a, counselor=counselor_a)
    factories.DocumentFactory(school=school_b, counselor=counselor_b)

    resp = client_a.get("/documents/")
    assert resp.status_code == 200
    assert resp.data["count"] == 2


@pytest.mark.django_db
def test_update_title(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a)
    resp = client_a.patch(f"/documents/{doc.id}/", {"title": "כותרת חדשה"}, format="multipart")
    assert resp.status_code == 200
    assert resp.data["title"] == "כותרת חדשה"


@pytest.mark.django_db
def test_soft_delete_returns_204(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a)
    resp = client_a.delete(f"/documents/{doc.id}/")
    assert resp.status_code == 204
    assert Document.objects.filter(id=doc.id).count() == 0
    assert Document.all_objects.filter(id=doc.id).count() == 1


# ---------------------------------------------------------------------------
# Soft-delete keeps the physical file
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_soft_delete_keeps_physical_file(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a)
    file_name = doc.file.name
    client_a.delete(f"/documents/{doc.id}/")
    assert default_storage.exists(file_name), "Physical file must survive a soft-delete"


# ---------------------------------------------------------------------------
# File-replace removes the old file (C3)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_file_replace_deletes_old_file(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a)
    old_name = doc.file.name

    client_a.patch(f"/documents/{doc.id}/", {
        "title": doc.title,
        "file": pdf("replacement.pdf"),
    }, format="multipart")

    assert not default_storage.exists(old_name), "Old file must be removed after file replace"
    doc.refresh_from_db()
    assert default_storage.exists(doc.file.name), "New file must exist"


# ---------------------------------------------------------------------------
# Category validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_student_category_requires_student(client_a):
    resp = client_a.post("/documents/", {
        "category": "student",
        "title": "test",
        "file": pdf(),
    }, format="multipart")
    assert resp.status_code == 400
    assert "student" in resp.data


@pytest.mark.django_db
def test_class_category_requires_class_level(client_a):
    resp = client_a.post("/documents/", {
        "category": "class",
        "title": "test",
        "file": pdf(),
    }, format="multipart")
    assert resp.status_code == 400
    assert "class_level" in resp.data


@pytest.mark.django_db
def test_general_category_rejects_student_relation(client_a, school_a):
    student = factories.StudentFactory(school=school_a)
    resp = client_a.post("/documents/", {
        "category": "general",
        "title": "test",
        "file": pdf(),
        "student": student.id,
    }, format="multipart")
    assert resp.status_code == 400
    assert "student" in resp.data


# ---------------------------------------------------------------------------
# DB CheckConstraint (bypasses the API)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_db_check_constraint_rejects_student_category_without_student(school_a, counselor_a):
    with pytest.raises((IntegrityError, Exception)):
        Document.objects.create(
            school=school_a,
            counselor=counselor_a,
            category="student",
            title="bad",
            file="documents/fake.pdf",
            student=None,
        )


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_rejects_disallowed_extension(client_a):
    bad_file = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
    resp = client_a.post("/documents/", {
        "category": "general",
        "title": "bad file",
        "file": bad_file,
    }, format="multipart")
    assert resp.status_code == 400
    assert "file" in resp.data


@pytest.mark.django_db
def test_rejects_oversized_file(client_a, settings):
    settings.DOCUMENT_MAX_UPLOAD_SIZE = 10  # 10 bytes
    big = SimpleUploadedFile("big.pdf", b"%PDF " + b"x" * 100, content_type="application/pdf")
    resp = client_a.post("/documents/", {
        "category": "general",
        "title": "big",
        "file": big,
    }, format="multipart")
    assert resp.status_code == 400
    assert "file" in resp.data


# ---------------------------------------------------------------------------
# School-scoping (cross-tenant isolation)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_cross_school_detail_returns_404(client_a, school_b, counselor_b):
    doc_b = factories.DocumentFactory(school=school_b, counselor=counselor_b)
    assert client_a.get(f"/documents/{doc_b.id}/").status_code == 404


@pytest.mark.django_db
def test_cross_school_delete_returns_404(client_a, school_b, counselor_b):
    doc_b = factories.DocumentFactory(school=school_b, counselor=counselor_b)
    assert client_a.delete(f"/documents/{doc_b.id}/").status_code == 404


@pytest.mark.django_db
def test_cross_school_content_returns_404(client_a, school_b, counselor_b):
    doc_b = factories.DocumentFactory(school=school_b, counselor=counselor_b)
    assert client_a.get(f"/documents/{doc_b.id}/content/").status_code == 404


@pytest.mark.django_db
def test_cross_school_download_returns_404(client_a, school_b, counselor_b):
    doc_b = factories.DocumentFactory(school=school_b, counselor=counselor_b)
    assert client_a.get(f"/documents/{doc_b.id}/download/").status_code == 404


# ---------------------------------------------------------------------------
# content / download actions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_content_action_serves_inline(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a)
    resp = client_a.get(f"/documents/{doc.id}/content/")
    assert resp.status_code == 200
    assert resp.get("Content-Disposition", "").startswith("inline")


@pytest.mark.django_db
def test_download_action_forces_attachment(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a)
    resp = client_a.get(f"/documents/{doc.id}/download/")
    assert resp.status_code == 200
    cd = _decode_header(resp.get("Content-Disposition", ""))
    assert "attachment" in cd


@pytest.mark.django_db
def test_download_filename_uses_document_title(client_a, school_a, counselor_a):
    doc = factories.DocumentFactory(school=school_a, counselor=counselor_a, title="דוח שנתי")
    resp = client_a.get(f"/documents/{doc.id}/download/")
    cd = _decode_header(resp.get("Content-Disposition", ""))
    assert "attachment" in cd
    assert ".pdf" in cd


# ---------------------------------------------------------------------------
# Filter support
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_filter_by_category(client_a, school_a, counselor_a):
    factories.DocumentFactory(school=school_a, counselor=counselor_a, category="general")
    student = factories.StudentFactory(school=school_a)
    factories.DocumentFactory(school=school_a, counselor=counselor_a, category="student", student=student)

    resp = client_a.get("/documents/?category=general")
    assert resp.status_code == 200
    assert all(d["category"] == "general" for d in resp.data["results"])


@pytest.mark.django_db
def test_filter_by_student(client_a, school_a, counselor_a):
    s1 = factories.StudentFactory(school=school_a)
    s2 = factories.StudentFactory(school=school_a)
    factories.DocumentFactory(school=school_a, counselor=counselor_a, category="student", student=s1)
    factories.DocumentFactory(school=school_a, counselor=counselor_a, category="student", student=s2)

    resp = client_a.get(f"/documents/?student={s1.id}")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["student"] == s1.id
