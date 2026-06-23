"""P1 — Lesson class assignments: assign, complete, update, delete, ?lesson
filter, and cross-school edges.
"""

import pytest

from core.models import LessonClassAssignment
from core.tests import factories


def _lesson(school, counselor, year):
    return factories.LessonPlanFactory(school=school, counselor=counselor, school_year=year)


# --- assign / CRUD ---------------------------------------------------------


@pytest.mark.django_db
def test_assign_class_succeeds_as_planned(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    payload = {
        "lesson": lesson.id,
        "class_level": class_levels[0].id,
        "class_number": 3,
    }

    resp = client_a.post("/lessonAssignments/", payload, format="json")
    assert resp.status_code == 201
    assert resp.data["status"] == "planned"
    assert resp.data["class_level_name"] == class_levels[0].name


@pytest.mark.django_db
def test_list_filtered_by_lesson(client_a, school_a, counselor_a, active_year, class_levels):
    lesson1 = _lesson(school_a, counselor_a, active_year)
    lesson2 = _lesson(school_a, counselor_a, active_year)
    factories.LessonClassAssignmentFactory(lesson=lesson1, class_level=class_levels[0])
    factories.LessonClassAssignmentFactory(lesson=lesson2, class_level=class_levels[1])

    resp = client_a.get(f"/lessonAssignments/?lesson={lesson1.id}")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["lesson"] == lesson1.id


@pytest.mark.django_db
def test_update_assignment_persists(client_a, school_a, counselor_a, active_year, class_levels):
    lesson = _lesson(school_a, counselor_a, active_year)
    assignment = factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_levels[0])

    resp = client_a.patch(
        f"/lessonAssignments/{assignment.id}/", {"class_number": 5}, format="json"
    )
    assert resp.status_code == 200
    assignment.refresh_from_db()
    assert assignment.class_number == 5


@pytest.mark.django_db
def test_delete_assignment_soft_deletes(client_a, school_a, counselor_a, active_year, class_levels):
    lesson = _lesson(school_a, counselor_a, active_year)
    assignment = factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_levels[0])

    resp = client_a.delete(f"/lessonAssignments/{assignment.id}/")
    assert resp.status_code == 204
    assert LessonClassAssignment.all_objects.get(id=assignment.id).deleted_at is not None


# --- complete action -------------------------------------------------------


@pytest.mark.django_db
def test_complete_sets_status_summary_and_default_date(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    assignment = factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_levels[0])

    resp = client_a.post(
        f"/lessonAssignments/{assignment.id}/complete/",
        {"summary": "סיכום השיעור"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "completed"
    assert resp.data["summary"] == "סיכום השיעור"
    # completed_date defaults to now when not supplied.
    assert resp.data["completed_date"] is not None


@pytest.mark.django_db
def test_complete_with_explicit_date(client_a, school_a, counselor_a, active_year, class_levels):
    lesson = _lesson(school_a, counselor_a, active_year)
    assignment = factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_levels[0])

    resp = client_a.post(
        f"/lessonAssignments/{assignment.id}/complete/",
        {"completed_date": "2026-03-01T10:00:00Z", "summary": "ok"},
        format="json",
    )
    assert resp.status_code == 200
    assignment.refresh_from_db()
    assert assignment.status == "completed"
    assert assignment.completed_date.date().isoformat() == "2026-03-01"


@pytest.mark.django_db
def test_complete_preserves_existing_summary_when_omitted(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    assignment = factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_levels[0], summary="סיכום קודם"
    )

    resp = client_a.post(f"/lessonAssignments/{assignment.id}/complete/", {}, format="json")
    assert resp.status_code == 200
    assert resp.data["status"] == "completed"
    assert resp.data["summary"] == "סיכום קודם"


# --- cross-school edges ----------------------------------------------------


@pytest.mark.django_db
def test_complete_other_school_assignment_404(
    client_a, school_b, counselor_b, active_year, class_levels
):
    lesson = _lesson(school_b, counselor_b, active_year)
    assignment = factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_levels[0])

    resp = client_a.post(f"/lessonAssignments/{assignment.id}/complete/", {}, format="json")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_assign_to_other_school_lesson_returns_500(
    client_a, school_b, counselor_b, active_year, class_levels
):
    """FINDING (latent bug): the assignment serializer's lesson queryset is global,
    so a cross-school lesson passes validation and reaches the service, where
    ensure_same_school raises a builtin PermissionError (not a DRF exception) ->
    unhandled 500. It should be a 400/403. Documented as current behavior."""
    other_lesson = _lesson(school_b, counselor_b, active_year)
    payload = {
        "lesson": other_lesson.id,
        "class_level": class_levels[0].id,
        "class_number": 1,
    }

    client_a.raise_request_exception = False
    resp = client_a.post("/lessonAssignments/", payload, format="json")
    assert resp.status_code == 500
