"""httpOnly-cookie refresh flow: login/refresh/rotation/logout.

The refresh token must never appear in a response body — only in an httpOnly
cookie scoped to /token — and rotation/logout must blacklist server-side.
"""

import pytest

from core.tests.factories import DEFAULT_PASSWORD
from core.views.auth import REFRESH_COOKIE, REFRESH_COOKIE_PATH

pytestmark = pytest.mark.django_db


def _login(api, counselor):
    return api.post(
        "/token/", {"username": counselor.user.username, "password": DEFAULT_PASSWORD}
    )


def test_login_sets_httponly_cookie_and_omits_refresh_from_body(api, counselor_a):
    resp = _login(api, counselor_a)
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" not in resp.data
    cookie = resp.cookies[REFRESH_COOKIE]
    assert cookie["httponly"]
    assert cookie["samesite"] == "Lax"
    assert cookie["path"] == REFRESH_COOKIE_PATH
    assert cookie.value  # actual token present


def test_refresh_from_cookie_returns_new_access(api, counselor_a):
    _login(api, counselor_a)
    resp = api.post("/token/refresh/", {})  # no body token — cookie only
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" not in resp.data  # rotated token goes to the cookie
    assert resp.cookies[REFRESH_COOKIE].value


def test_refresh_without_cookie_or_body_is_rejected(api):
    resp = api.post("/token/refresh/", {})
    assert resp.status_code == 401


def test_rotation_blacklists_previous_refresh_token(api, counselor_a):
    old = _login(api, counselor_a).cookies[REFRESH_COOKIE].value
    api.post("/token/refresh/", {})  # rotates; old token must now be dead
    resp = api.post("/token/refresh/", {"refresh": old})
    assert resp.status_code == 401


def test_logout_blacklists_token_and_expires_cookie(api, counselor_a):
    token = _login(api, counselor_a).cookies[REFRESH_COOKIE].value
    resp = api.post("/token/logout/", {})
    assert resp.status_code == 200
    dropped = resp.cookies[REFRESH_COOKIE]
    assert dropped.value == ""
    assert dropped["max-age"] == 0
    # replaying the blacklisted token must fail
    resp = api.post("/token/refresh/", {"refresh": token})
    assert resp.status_code == 401


def test_logout_without_cookie_still_succeeds(api):
    resp = api.post("/token/logout/", {})
    assert resp.status_code == 200
