"""Tests that the custom JWT serializer includes is_staff in the token payload."""

import base64
import json

import pytest
from rest_framework.test import APIClient

from core.tests.factories import AdminUserFactory, CounselorFactory, DEFAULT_PASSWORD


def _decode_payload(token: str) -> dict:
    payload_b64 = token.split(".")[1]
    # Add padding so b64decode doesn't complain.
    padding = 4 - len(payload_b64) % 4
    payload_b64 += "=" * (padding % 4)
    return json.loads(base64.b64decode(payload_b64))


@pytest.mark.django_db
def test_admin_token_has_is_staff_true():
    admin = AdminUserFactory()
    client = APIClient()
    resp = client.post("/token/", {"username": admin.username, "password": DEFAULT_PASSWORD})
    assert resp.status_code == 200
    payload = _decode_payload(resp.data["access"])
    assert payload["is_staff"] is True
    assert payload["has_counselor"] is False


@pytest.mark.django_db
def test_counselor_token_has_is_staff_false():
    counselor = CounselorFactory()
    client = APIClient()
    resp = client.post(
        "/token/", {"username": counselor.user.username, "password": DEFAULT_PASSWORD}
    )
    assert resp.status_code == 200
    payload = _decode_payload(resp.data["access"])
    assert payload["is_staff"] is False
    assert payload["has_counselor"] is True


@pytest.mark.django_db
def test_hybrid_token_has_is_staff_and_has_counselor_true():
    """A user who is both is_staff and has a Counselor row (not reachable via
    the app today, but not prevented at the DB level either) gets both claims
    set — the client uses this to show both the admin and counselor nav."""
    hybrid_counselor = CounselorFactory(user=AdminUserFactory())
    client = APIClient()
    resp = client.post(
        "/token/",
        {"username": hybrid_counselor.user.username, "password": DEFAULT_PASSWORD},
    )
    assert resp.status_code == 200
    payload = _decode_payload(resp.data["access"])
    assert payload["is_staff"] is True
    assert payload["has_counselor"] is True
