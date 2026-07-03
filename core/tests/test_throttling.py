"""Rate limiting on the auth endpoints (login 5/min, refresh 10/min per IP).

The suite-wide ``_no_throttling`` fixture nulls the scoped rates so unrelated
tests never trip them; each fixture here re-enables one scope with a tiny
window and clears the shared locmem cache around the test.
"""

import pytest
from django.core.cache import cache
from rest_framework.throttling import SimpleRateThrottle

from core.tests.factories import DEFAULT_PASSWORD

pytestmark = pytest.mark.django_db


@pytest.fixture
def login_throttle(monkeypatch):
    monkeypatch.setitem(SimpleRateThrottle.THROTTLE_RATES, "login", "3/min")
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def refresh_throttle(monkeypatch):
    monkeypatch.setitem(SimpleRateThrottle.THROTTLE_RATES, "token_refresh", "3/min")
    cache.clear()
    yield
    cache.clear()


def test_login_returns_429_after_limit(api, login_throttle):
    for _ in range(3):
        resp = api.post("/token/", {"username": "ghost", "password": "wrong"})
        assert resp.status_code == 401
    resp = api.post("/token/", {"username": "ghost", "password": "wrong"})
    assert resp.status_code == 429


def test_login_allowed_under_limit(api, counselor_a, login_throttle):
    resp = api.post(
        "/token/", {"username": counselor_a.user.username, "password": DEFAULT_PASSWORD}
    )
    assert resp.status_code == 200


def test_refresh_returns_429_after_limit(api, refresh_throttle):
    for _ in range(3):
        resp = api.post("/token/refresh/", {"refresh": "not-a-token"})
        assert resp.status_code == 401
    resp = api.post("/token/refresh/", {"refresh": "not-a-token"})
    assert resp.status_code == 429
