"""Tests for the SupportRequest feature: creation, email notification, listing, resolve."""

import pytest
from django.core import mail

from core.models import SupportRequest
from core.tests.factories import CounselorFactory, SupportRequestFactory


URL_LIST = "/support/"


def url_detail(pk):
    return f"/support/{pk}/"


def url_resolve(pk):
    return f"/support/{pk}/resolve/"


# ---------------------------------------------------------------------------
# Create (counselor)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_counselor_can_create_request(client_a, counselor_a):
    resp = client_a.post(URL_LIST, {"subject": "בעיה טכנית", "message": "משהו לא עובד"})
    assert resp.status_code == 201
    assert SupportRequest.objects.filter(school=counselor_a.school).count() == 1


@pytest.mark.django_db
def test_create_request_sends_email(client_a, settings):
    settings.ADMIN_EMAIL = "admin@example.com"
    client_a.post(URL_LIST, {"subject": "נושא", "message": "תוכן"})
    assert len(mail.outbox) == 1
    assert "admin@example.com" in mail.outbox[0].to
    assert "נושא" in mail.outbox[0].subject


@pytest.mark.django_db
def test_new_request_has_open_status(client_a):
    resp = client_a.post(URL_LIST, {"subject": "שאלה", "message": "?"})
    assert resp.data["status"] == SupportRequest.STATUS_OPEN


@pytest.mark.django_db
def test_unauthenticated_cannot_create(api):
    resp = api.post(URL_LIST, {"subject": "test", "message": "test"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# List (admin-only)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_admin_can_list_all_requests(admin_client, counselor_a, counselor_b, school_a, school_b):
    SupportRequestFactory(counselor=counselor_a, school=school_a)
    SupportRequestFactory(counselor=counselor_b, school=school_b)
    resp = admin_client.get(URL_LIST)
    assert resp.status_code == 200
    # Unpaginated: the admin support page filters client-side via tabs over
    # the whole list, with no pagination UI.
    assert len(resp.data) == 2


@pytest.mark.django_db
def test_counselor_cannot_list_requests(client_a):
    resp = client_a.get(URL_LIST)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_unauthenticated_cannot_list(api):
    resp = api.get(URL_LIST)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Resolve (admin-only)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_admin_can_resolve_request(admin_client, counselor_a, school_a):
    req = SupportRequestFactory(counselor=counselor_a, school=school_a)
    resp = admin_client.post(url_resolve(req.pk))
    assert resp.status_code == 200
    req.refresh_from_db()
    assert req.status == SupportRequest.STATUS_RESOLVED


@pytest.mark.django_db
def test_counselor_cannot_resolve_request(client_a, counselor_a, school_a):
    req = SupportRequestFactory(counselor=counselor_a, school=school_a)
    resp = client_a.post(url_resolve(req.pk))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_resolve_response_contains_updated_status(admin_client, counselor_a, school_a):
    req = SupportRequestFactory(counselor=counselor_a, school=school_a)
    resp = admin_client.post(url_resolve(req.pk))
    assert resp.data["status"] == SupportRequest.STATUS_RESOLVED
