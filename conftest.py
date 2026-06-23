"""Project-wide pytest configuration: test-environment guards + shared fixtures.

Note: the APScheduler reminder job is already test-safe — ``CoreConfig.ready``
only starts it when ``'runserver' in sys.argv``, which is never true under
pytest, so no scheduler runs during tests.

Fixture layout
--------------
Two tenants (``school_a`` / ``school_b``) with a counselor each, an admin user,
and the immutable academic data (``class_levels``, ``active_year``). Auth is
provided through the ``auth_client`` factory-fixture, which issues a real JWT so
the authentication path is exercised; ``client_a`` / ``client_b`` / ``admin_client``
are ready-made shortcuts.
"""

import pytest
from core.tests import factories
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture(autouse=True)
def _use_locmem_email(settings):
    """Never touch real SMTP during tests; capture mail in memory instead."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture(autouse=True)
def _fast_password_hashing(settings):
    """Use a cheap hasher so the many factory-built users don't dominate runtime.

    Applied before factories create users; /token/ login still works because
    check_password reads the algorithm from the stored hash.
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# --- Unauthenticated client ------------------------------------------------


@pytest.fixture
def api():
    """A bare, unauthenticated APIClient."""
    return APIClient()


# --- Academic reference data ----------------------------------------------


@pytest.fixture
def class_levels(db):
    """All eight grade levels (א..ח), returned in order."""
    return [factories.ClassLevelFactory(name=name) for name in factories.GRADE_LEVELS]


@pytest.fixture
def active_year(db):
    """The single active SchoolYear most endpoints assume exists."""
    return factories.SchoolYearFactory(name="2025-2026", is_active=True)


# --- Tenants and users -----------------------------------------------------


@pytest.fixture
def school_a(db):
    return factories.SchoolFactory(name="בית ספר א")


@pytest.fixture
def school_b(db):
    return factories.SchoolFactory(name="בית ספר ב")


@pytest.fixture
def counselor_a(db, school_a):
    return factories.CounselorFactory(school=school_a)


@pytest.fixture
def counselor_b(db, school_b):
    return factories.CounselorFactory(school=school_b)


@pytest.fixture
def admin_user(db):
    return factories.AdminUserFactory()


# --- Authenticated clients -------------------------------------------------


@pytest.fixture
def auth_client():
    """Factory: return an APIClient authenticated as the given user.

    Accepts a Counselor (uses its ``.user``) or a plain User. Issues a real JWT
    via the Bearer header so the SimpleJWT auth path is exercised end to end.
    """

    def _make(user_or_counselor):
        user = getattr(user_or_counselor, "user", user_or_counselor)
        client = APIClient()
        token = RefreshToken.for_user(user).access_token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    return _make


@pytest.fixture
def client_a(auth_client, counselor_a):
    """Authenticated client for the counselor of school A."""
    return auth_client(counselor_a)


@pytest.fixture
def client_b(auth_client, counselor_b):
    """Authenticated client for the counselor of school B."""
    return auth_client(counselor_b)


@pytest.fixture
def admin_client(auth_client, admin_user):
    """Authenticated client for an is_staff admin user."""
    return auth_client(admin_user)
