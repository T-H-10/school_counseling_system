"""P1 — Dashboard at-risk alert: automatic 90-day rule + manual follow-up flag."""

from datetime import timedelta

import pytest
from django.utils import timezone

from core.tests import factories


@pytest.mark.django_db
def test_at_risk_includes_manually_flagged_student_with_recent_contact(
    client_a, school_a, counselor_a
):
    student = factories.StudentFactory(school=school_a, follow_up_level="at_risk")
    factories.StudentEventFactory(
        student=student, counselor=counselor_a, school=school_a, date=timezone.now()
    )

    resp = client_a.get("/dashboard/")

    assert resp.status_code == 200
    at_risk = resp.data["alerts"]["at_risk_students"]
    assert at_risk["count"] == 1
    assert at_risk["students"][0]["id"] == str(student.id)


@pytest.mark.django_db
def test_student_with_recent_contact_and_no_flag_is_not_at_risk(
    client_a, school_a, counselor_a
):
    student = factories.StudentFactory(school=school_a, follow_up_level="none")
    factories.StudentEventFactory(
        student=student, counselor=counselor_a, school=school_a, date=timezone.now()
    )

    resp = client_a.get("/dashboard/")

    at_risk = resp.data["alerts"]["at_risk_students"]
    assert at_risk["count"] == 0


@pytest.mark.django_db
def test_student_with_stale_contact_and_no_flag_is_at_risk(client_a, school_a, counselor_a):
    student = factories.StudentFactory(school=school_a, follow_up_level="none")
    factories.StudentEventFactory(
        student=student,
        counselor=counselor_a,
        school=school_a,
        date=timezone.now() - timedelta(days=100),
    )

    resp = client_a.get("/dashboard/")

    at_risk = resp.data["alerts"]["at_risk_students"]
    assert at_risk["count"] == 1
