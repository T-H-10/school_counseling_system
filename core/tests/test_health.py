"""The /healthz/ liveness probe: anonymous, DB-free, always 200."""

import pytest


def test_healthz_is_public_and_ok(api):
    resp = api.get("/healthz/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
def test_healthz_needs_no_database(api, django_assert_num_queries):
    with django_assert_num_queries(0):
        resp = api.get("/healthz/")
    assert resp.status_code == 200
