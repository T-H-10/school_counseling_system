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
