"""Step 1 harness sanity checks.

These prove the pytest-django wiring works end to end: project settings are
loaded and the test database spins up and is queryable. The real API suite
replaces/augments these in later steps.
"""

import pytest


@pytest.mark.smoke
def test_django_settings_loaded(settings):
    """pytest-django loaded the project settings (config.settings)."""
    assert settings.LANGUAGE_CODE == "he"
    assert settings.TIME_ZONE == "Asia/Jerusalem"


@pytest.mark.smoke
def test_email_backend_is_locmem(settings):
    """The autouse guard redirected email away from real SMTP."""
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"


@pytest.mark.smoke
@pytest.mark.django_db
def test_database_available():
    """The test database is created and the ORM is queryable."""
    from django.contrib.auth.models import User

    assert User.objects.count() == 0


@pytest.mark.smoke
@pytest.mark.django_db
def test_token_obtain_happy_path(api, counselor_a):
    """A factory-built counselor can log in via /token/ (proves password hashing
    and the SchoolFactory/CounselorFactory/UserFactory chain)."""
    from core.tests.factories import DEFAULT_PASSWORD

    resp = api.post(
        "/token/",
        {"username": counselor_a.user.username, "password": DEFAULT_PASSWORD},
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


@pytest.mark.smoke
@pytest.mark.django_db
def test_auth_client_reaches_protected_endpoint(client_a):
    """The auth_client JWT fixture authorizes an IsCounselor endpoint and the
    school-scoped queryset returns an (empty) paginated list."""
    resp = client_a.get("/students/")
    assert resp.status_code == 200
    assert resp.data["count"] == 0


@pytest.mark.smoke
@pytest.mark.django_db
def test_class_levels_and_active_year_fixtures(class_levels, active_year):
    """The reference-data fixtures seed all eight grades and one active year."""
    assert [lvl.name for lvl in class_levels] == list("אבגדהוזח")
    assert active_year.is_active is True
