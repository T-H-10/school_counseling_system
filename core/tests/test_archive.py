"""Admin-only archive/restore across the 5 soft-deletable entities.

Covers: permission matrix, per-entity list+restore round trip, cross-school
filtering, the orphan-prevention integrity check, and error cases.
"""

import pytest

from core.tests import factories

pytestmark = pytest.mark.django_db

ENTITY_KEYS = ["students", "enrollments", "studentEvents", "lessons", "lessonAssignments"]

# One factory per entity, matching core.services.archive_service.ENTITY_MODELS.
FACTORIES = {
    "students": factories.StudentFactory,
    "enrollments": factories.StudentEnrollmentFactory,
    "studentEvents": factories.StudentEventFactory,
    "lessons": factories.LessonPlanFactory,
    "lessonAssignments": factories.LessonClassAssignmentFactory,
}

# The list endpoint each entity is normally visible through, once alive.
NORMAL_ENDPOINTS = {
    "students": "/students/",
    "enrollments": "/enrollments/",
    "studentEvents": "/studentEvents/",
    "lessons": "/lessons/",
    "lessonAssignments": "/lessonAssignments/",
}


def _build(entity_key, school, counselor, school_year, class_level):
    """Build one alive instance of ``entity_key`` inside ``school``."""
    if entity_key == "students":
        return factories.StudentFactory(school=school)
    if entity_key == "enrollments":
        student = factories.StudentFactory(school=school)
        return factories.StudentEnrollmentFactory(
            student=student, school_year=school_year, class_level=class_level
        )
    if entity_key == "studentEvents":
        student = factories.StudentFactory(school=school)
        return factories.StudentEventFactory(student=student, counselor=counselor)
    if entity_key == "lessons":
        return factories.LessonPlanFactory(school=school, counselor=counselor, school_year=school_year)
    if entity_key == "lessonAssignments":
        lesson = factories.LessonPlanFactory(school=school, counselor=counselor, school_year=school_year)
        return factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_level)
    raise ValueError(entity_key)


# --- Permission matrix -------------------------------------------------------


def test_anonymous_is_rejected(api):
    assert api.get("/archive/?entity_type=students").status_code == 401
    assert api.post("/archive/1/restore/?entity_type=students").status_code == 401


def test_counselor_forbidden(client_a):
    assert client_a.get("/archive/?entity_type=students").status_code == 403
    assert client_a.post("/archive/1/restore/?entity_type=students").status_code == 403


def test_admin_allowed(admin_client):
    assert admin_client.get("/archive/?entity_type=students").status_code == 200


# --- Per-entity list + restore round trip -----------------------------------


@pytest.mark.parametrize("entity_key", ENTITY_KEYS)
def test_soft_deleted_row_appears_in_archive_and_disappears_from_normal_list(
    admin_client, client_a, school_a, counselor_a, active_year, class_levels, entity_key
):
    obj = _build(entity_key, school_a, counselor_a, active_year, class_levels[0])
    obj.delete()  # soft delete

    normal_resp = client_a.get(NORMAL_ENDPOINTS[entity_key])
    assert normal_resp.status_code == 200
    assert all(row["id"] != obj.id for row in normal_resp.data["results"])

    archive_resp = admin_client.get(f"/archive/?entity_type={entity_key}")
    assert archive_resp.status_code == 200
    ids = [row["id"] for row in archive_resp.data["results"]]
    assert obj.id in ids


@pytest.mark.parametrize("entity_key", ENTITY_KEYS)
def test_restore_reverses_soft_delete(
    admin_client, client_a, school_a, counselor_a, active_year, class_levels, entity_key
):
    obj = _build(entity_key, school_a, counselor_a, active_year, class_levels[0])
    obj.delete()

    resp = admin_client.post(f"/archive/{obj.id}/restore/?entity_type={entity_key}")
    assert resp.status_code == 200
    assert resp.data["is_restorable"] is True

    normal_resp = client_a.get(NORMAL_ENDPOINTS[entity_key])
    assert any(row["id"] == obj.id for row in normal_resp.data["results"])

    archive_resp = admin_client.get(f"/archive/?entity_type={entity_key}")
    assert all(row["id"] != obj.id for row in archive_resp.data["results"])


def test_restoring_already_alive_row_is_a_no_op_success(admin_client, school_a):
    student = factories.StudentFactory(school=school_a)
    resp = admin_client.post(f"/archive/{student.id}/restore/?entity_type=students")
    assert resp.status_code == 200
    student.refresh_from_db()
    assert student.deleted_at is None


# --- Cross-school filtering --------------------------------------------------


def test_school_filter_scopes_archive_list(admin_client, school_a, school_b, counselor_a, counselor_b):
    student_a = factories.StudentFactory(school=school_a)
    student_a.delete()
    student_b = factories.StudentFactory(school=school_b)
    student_b.delete()

    resp = admin_client.get(f"/archive/?entity_type=students&school={school_a.id}")
    assert resp.status_code == 200
    ids = [row["id"] for row in resp.data["results"]]
    assert student_a.id in ids
    assert student_b.id not in ids

    resp = admin_client.get("/archive/?entity_type=students")
    ids = [row["id"] for row in resp.data["results"]]
    assert student_a.id in ids
    assert student_b.id in ids


# --- Integrity check (orphan prevention) -------------------------------------


def test_archived_child_of_deleted_parent_is_not_restorable(admin_client, school_a, counselor_a):
    student = factories.StudentFactory(school=school_a)
    event = factories.StudentEventFactory(student=student, counselor=counselor_a)
    event.delete()
    student.delete()

    resp = admin_client.get("/archive/?entity_type=studentEvents")
    row = next(r for r in resp.data["results"] if r["id"] == event.id)
    assert row["is_restorable"] is False
    assert row["blocked_reason"]

    restore_resp = admin_client.post(f"/archive/{event.id}/restore/?entity_type=studentEvents")
    assert restore_resp.status_code == 400


def test_restoring_parent_first_unblocks_child(admin_client, school_a, counselor_a):
    student = factories.StudentFactory(school=school_a)
    event = factories.StudentEventFactory(student=student, counselor=counselor_a)
    event.delete()
    student.delete()

    restore_student = admin_client.post(f"/archive/{student.id}/restore/?entity_type=students")
    assert restore_student.status_code == 200

    resp = admin_client.get("/archive/?entity_type=studentEvents")
    row = next(r for r in resp.data["results"] if r["id"] == event.id)
    assert row["is_restorable"] is True
    assert row["blocked_reason"] is None

    restore_event = admin_client.post(f"/archive/{event.id}/restore/?entity_type=studentEvents")
    assert restore_event.status_code == 200


def test_restore_does_not_cascade_to_related_soft_deleted_rows(
    admin_client, school_a, counselor_a, active_year, class_levels
):
    """Restoring a Student must not resurrect its own soft-deleted enrollment."""
    student = factories.StudentFactory(school=school_a)
    enrollment = factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[0]
    )
    enrollment.delete()
    student.delete()

    resp = admin_client.post(f"/archive/{student.id}/restore/?entity_type=students")
    assert resp.status_code == 200

    enrollment.refresh_from_db()
    assert enrollment.deleted_at is not None


# --- Error cases --------------------------------------------------------------


def test_missing_entity_type_returns_400(admin_client):
    assert admin_client.get("/archive/").status_code == 400
    assert admin_client.post("/archive/1/restore/").status_code == 400


def test_invalid_entity_type_returns_400(admin_client):
    assert admin_client.get("/archive/?entity_type=bogus").status_code == 400


def test_restoring_nonexistent_id_returns_404(admin_client):
    resp = admin_client.post("/archive/999999/restore/?entity_type=students")
    assert resp.status_code == 404


def test_summary_returns_counts_per_entity(admin_client, school_a):
    student = factories.StudentFactory(school=school_a)
    student.delete()

    resp = admin_client.get("/archive/summary/")
    assert resp.status_code == 200
    assert resp.data["students"] >= 1
    assert set(resp.data.keys()) == set(ENTITY_KEYS)
