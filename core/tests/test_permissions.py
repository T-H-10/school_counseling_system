"""P0 — authorization matrix and cross-school (tenant) isolation.

The single most important property of this API: every counselor endpoint is
scoped to ``request.user.counselor.school`` via ``BaseSchoolViewSet``, and the
permission tiers (IsCounselor / IsAdminUser / IsAuthenticated) gate access.
These tests sweep roles against endpoints and assert one school can never reach
another's objects.

Documented quirks (asserted as real behavior):
- ``IsCounselor`` has no admin bypass, so a plain is_staff admin (no Counselor
  profile) gets 403 on counselor endpoints — "admin = unrestricted" does NOT
  hold for them.
- Cross-school object access returns 404 (filtered out of the queryset), not
  403, because scoping happens before object-level checks.
"""
import pytest

from core.tests import factories

pytestmark = pytest.mark.permissions

# Endpoints grouped by the permission tier guarding them.
COUNSELOR_ENDPOINTS = [
    "/students/",
    "/enrollments/",
    "/studentEvents/",
    "/lessons/",
    "/lessonAssignments/",
    "/dashboard/",
]
ADMIN_ENDPOINTS = ["/schools/", "/counselors/"]
AUTHENTICATED_ENDPOINTS = ["/classLevels/", "/schoolYears/"]

ALL_PROTECTED = COUNSELOR_ENDPOINTS + ADMIN_ENDPOINTS + AUTHENTICATED_ENDPOINTS

# Resources whose detail routes are school-scoped through BaseSchoolViewSet.
SCOPED_RESOURCES = [
    "students",
    "enrollments",
    "studentEvents",
    "lessons",
    "lessonAssignments",
]


def _make_objects_in_school(school, counselor, school_year, class_level):
    """Create one object of every scoped resource inside ``school``.

    Returns a dict keyed by the URL resource name so tests can pick any one.
    """
    student = factories.StudentFactory(school=school)
    enrollment = factories.StudentEnrollmentFactory(
        student=student, school_year=school_year, class_level=class_level
    )
    event = factories.StudentEventFactory(student=student, counselor=counselor)
    lesson = factories.LessonPlanFactory(
        school=school, counselor=counselor, school_year=school_year
    )
    assignment = factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_level
    )
    return {
        "students": student,
        "enrollments": enrollment,
        "studentEvents": event,
        "lessons": lesson,
        "lessonAssignments": assignment,
    }


# --- Anonymous -------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("url", ALL_PROTECTED)
def test_anonymous_is_rejected(api, url):
    """No credentials -> 401 on every protected endpoint."""
    assert api.get(url).status_code == 401


# --- Authenticated user without a Counselor profile ------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("url", COUNSELOR_ENDPOINTS + ADMIN_ENDPOINTS)
def test_plain_user_forbidden_on_counselor_and_admin_endpoints(auth_client, url):
    """A logged-in user who is neither counselor nor admin -> 403."""
    client = auth_client(factories.UserFactory())
    assert client.get(url).status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("url", AUTHENTICATED_ENDPOINTS)
def test_plain_user_allowed_on_authenticated_endpoints(auth_client, url):
    """classLevels and schoolYears reads are open to any authenticated user."""
    client = auth_client(factories.UserFactory())
    assert client.get(url).status_code == 200


# --- Counselor -------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("url", COUNSELOR_ENDPOINTS + AUTHENTICATED_ENDPOINTS)
def test_counselor_allowed_on_own_endpoints(client_a, url):
    assert client_a.get(url).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url", ADMIN_ENDPOINTS)
def test_counselor_forbidden_on_admin_endpoints(client_a, url):
    assert client_a.get(url).status_code == 403


# --- Admin (is_staff, no Counselor profile) --------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("url", ADMIN_ENDPOINTS + AUTHENTICATED_ENDPOINTS)
def test_admin_allowed_on_admin_and_authenticated_endpoints(admin_client, url):
    assert admin_client.get(url).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("url", COUNSELOR_ENDPOINTS)
def test_admin_without_counselor_forbidden_on_counselor_endpoints(admin_client, url):
    """IsCounselor has no admin bypass: a counselor-less admin is denied."""
    assert admin_client.get(url).status_code == 403


# --- Cross-school (tenant) isolation ---------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("resource", SCOPED_RESOURCES)
def test_counselor_cannot_retrieve_other_school_object(
    resource, client_a, school_b, counselor_b, active_year, class_levels
):
    """School A's counselor gets 404 retrieving any of school B's objects."""
    objs = _make_objects_in_school(school_b, counselor_b, active_year, class_levels[0])
    resp = client_a.get(f"/{resource}/{objs[resource].id}/")
    assert resp.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("resource", SCOPED_RESOURCES)
def test_counselor_cannot_delete_other_school_object(
    resource, client_a, school_b, counselor_b, active_year, class_levels
):
    """School A's counselor gets 404 deleting any of school B's objects."""
    objs = _make_objects_in_school(school_b, counselor_b, active_year, class_levels[0])
    resp = client_a.delete(f"/{resource}/{objs[resource].id}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_student_list_is_scoped_to_own_school(
    client_a, school_a, school_b, counselor_a, counselor_b, active_year, class_levels
):
    """Listing returns only the caller's school, never the other tenant's rows."""
    _make_objects_in_school(school_a, counselor_a, active_year, class_levels[0])
    _make_objects_in_school(school_b, counselor_b, active_year, class_levels[0])

    resp = client_a.get("/students/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
