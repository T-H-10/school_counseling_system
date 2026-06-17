"""Project-wide pytest configuration.

Fixtures and factories for the API test suite are added here in Step 2. For
now this only holds the test-environment guards.

Note: the APScheduler reminder job is already test-safe — ``CoreConfig.ready``
only starts it when ``'runserver' in sys.argv``, which is never true under
pytest, so no scheduler runs during tests.
"""
import pytest


@pytest.fixture(autouse=True)
def _use_locmem_email(settings):
    """Never touch real SMTP during tests; capture mail in memory instead."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
