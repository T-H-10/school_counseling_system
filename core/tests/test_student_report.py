"""Tests for the per-student report aggregation (StudentReportService)."""

from datetime import datetime

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.models import Document
from core.services.student_report_service import StudentReportService
from core.tests import factories


def _aware(year, month, day, hour=10):
    return timezone.make_aware(
        datetime(year, month, day, hour), timezone.get_default_timezone()
    )


# --- service ----------------------------------------------------------------


@pytest.mark.django_db
def test_report_full_shape(counselor_a, active_year, class_levels):
    student = factories.StudentFactory(school=counselor_a.school)
    factories.StudentEnrollmentFactory(
        student=student,
        school_year=active_year,
        class_level=class_levels[1],
        class_number=2,
        teacher_name="מורה א",
    )
    factories.StudentEventFactory(student=student, counselor=counselor_a, title="שיחה")
    factories.DocumentFactory(
        school=counselor_a.school, counselor=counselor_a, category="student", student=student
    )
    # A general document must not leak into the student report.
    factories.DocumentFactory(school=counselor_a.school, counselor=counselor_a)

    report = StudentReportService.get_report(counselor_a.user, student)

    assert report["school"]["name"] == counselor_a.school.name
    assert report["school"]["institution_code"] == counselor_a.school.institution_code
    assert report["counselor"]["full_name"] == counselor_a.full_name
    assert report["year_filter"] is None
    assert report["generated_at"] is not None
    assert report["student"]["full_name"] == student.full_name
    assert report["student"]["id_number"] == student.id_number

    assert [e["school_year_name"] for e in report["enrollments"]] == [active_year.name]
    assert report["enrollments"][0]["class_level_name"] == class_levels[1].name
    assert report["enrollments"][0]["teacher_name"] == "מורה א"

    assert len(report["events"]) == 1
    assert report["events"][0]["title"] == "שיחה"
    assert report["events"][0]["status"] == "pending"

    assert len(report["documents"]) == 1
    assert report["documents"][0]["display_date"]


@pytest.mark.django_db
def test_report_enrollments_newest_year_first(counselor_a, active_year, class_levels):
    prev_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=counselor_a.school)
    factories.StudentEnrollmentFactory(
        student=student, school_year=prev_year, class_level=class_levels[0]
    )
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[1]
    )

    report = StudentReportService.get_report(counselor_a.user, student)

    assert [e["school_year_name"] for e in report["enrollments"]] == [
        active_year.name,
        prev_year.name,
    ]


@pytest.mark.django_db
def test_report_year_filter_events_and_enrollments(counselor_a, active_year, class_levels):
    prev_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=counselor_a.school)
    factories.StudentEnrollmentFactory(
        student=student, school_year=prev_year, class_level=class_levels[0]
    )
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[1]
    )
    # 2025-2026 runs Sep 1 2025 – Aug 31 2026.
    in_range = factories.StudentEventFactory(
        student=student, counselor=counselor_a, date=_aware(2025, 10, 1)
    )
    factories.StudentEventFactory(
        student=student, counselor=counselor_a, date=_aware(2025, 5, 1)
    )

    report = StudentReportService.get_report(
        counselor_a.user, student, school_year=active_year
    )

    assert report["year_filter"] == {"id": active_year.id, "name": active_year.name}
    assert [e["id"] for e in report["events"]] == [in_range.id]
    assert [e["school_year_name"] for e in report["enrollments"]] == [active_year.name]


@pytest.mark.django_db
def test_report_year_filter_documents_by_date(counselor_a, active_year):
    student = factories.StudentFactory(school=counselor_a.school)
    in_range = factories.DocumentFactory(
        school=counselor_a.school, counselor=counselor_a, category="student", student=student
    )
    Document.objects.filter(pk=in_range.pk).update(created_at=_aware(2025, 10, 1))
    out_of_range = factories.DocumentFactory(
        school=counselor_a.school, counselor=counselor_a, category="student", student=student
    )
    Document.objects.filter(pk=out_of_range.pk).update(created_at=_aware(2025, 5, 1))

    report = StudentReportService.get_report(
        counselor_a.user, student, school_year=active_year
    )

    assert [d["id"] for d in report["documents"]] == [in_range.id]


@pytest.mark.django_db
def test_year_date_range_boundaries(db):
    year = factories.SchoolYearFactory(name="2025-2026")
    start, end = StudentReportService.year_date_range(year)
    local_start = timezone.localtime(start)
    local_end = timezone.localtime(end)
    assert (local_start.year, local_start.month, local_start.day) == (2025, 9, 1)
    assert (local_end.year, local_end.month, local_end.day) == (2026, 8, 31)


@pytest.mark.django_db
def test_report_invalid_year_name_raises(counselor_a):
    bad_year = factories.SchoolYearFactory(name="תשפו")
    student = factories.StudentFactory(school=counselor_a.school)

    with pytest.raises(ValidationError) as exc:
        StudentReportService.get_report(counselor_a.user, student, school_year=bad_year)

    assert "year" in exc.value.detail


@pytest.mark.django_db
def test_report_cross_school_denied(counselor_a, counselor_b):
    student = factories.StudentFactory(school=counselor_a.school)

    with pytest.raises(PermissionError):
        StudentReportService.get_report(counselor_b.user, student)


# --- endpoint ---------------------------------------------------------------


@pytest.mark.django_db
def test_report_endpoint_returns_full_shape(client_a, counselor_a, active_year, class_levels):
    student = factories.StudentFactory(school=counselor_a.school)
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[0]
    )
    factories.StudentEventFactory(student=student, counselor=counselor_a)

    resp = client_a.get(f"/students/{student.id}/report/")

    assert resp.status_code == 200
    assert resp.data["student"]["full_name"] == student.full_name
    assert resp.data["school"]["name"] == counselor_a.school.name
    assert resp.data["counselor"]["full_name"] == counselor_a.full_name
    assert resp.data["year_filter"] is None
    assert len(resp.data["enrollments"]) == 1
    assert len(resp.data["events"]) == 1
    assert resp.data["documents"] == []


@pytest.mark.django_db
def test_report_endpoint_year_filter(client_a, counselor_a, active_year, class_levels):
    student = factories.StudentFactory(school=counselor_a.school)
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[0]
    )
    in_range = factories.StudentEventFactory(
        student=student, counselor=counselor_a, date=_aware(2025, 10, 1)
    )
    factories.StudentEventFactory(
        student=student, counselor=counselor_a, date=_aware(2025, 5, 1)
    )

    resp = client_a.get(f"/students/{student.id}/report/", {"year": active_year.id})

    assert resp.status_code == 200
    assert resp.data["year_filter"]["name"] == active_year.name
    assert [e["id"] for e in resp.data["events"]] == [in_range.id]


@pytest.mark.django_db
def test_report_endpoint_invalid_year_returns_400(client_a, counselor_a):
    student = factories.StudentFactory(school=counselor_a.school)

    resp = client_a.get(f"/students/{student.id}/report/", {"year": "abc"})
    assert resp.status_code == 400
    assert "year" in resp.data

    resp = client_a.get(f"/students/{student.id}/report/", {"year": 999999})
    assert resp.status_code == 400
    assert "year" in resp.data


@pytest.mark.django_db
def test_report_endpoint_cross_school_404(client_b, counselor_a):
    student = factories.StudentFactory(school=counselor_a.school)

    resp = client_b.get(f"/students/{student.id}/report/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_report_endpoint_requires_auth(api, counselor_a):
    student = factories.StudentFactory(school=counselor_a.school)

    resp = api.get(f"/students/{student.id}/report/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_report_endpoint_admin_without_counselor_403(admin_client, counselor_a):
    student = factories.StudentFactory(school=counselor_a.school)

    resp = admin_client.get(f"/students/{student.id}/report/")
    assert resp.status_code == 403
