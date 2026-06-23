"""P1 — Lessons: CRUD, ordering, nested assignments, the calendar action, and
cascade soft-delete of assignments.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from core.models import LessonClassAssignment, LessonPlan
from core.tests import factories


def _lesson(school, counselor, year, **kwargs):
    return factories.LessonPlanFactory(
        school=school, counselor=counselor, school_year=year, **kwargs
    )


# --- CRUD ------------------------------------------------------------------


@pytest.mark.django_db
def test_create_lesson_succeeds(client_a, active_year):
    payload = {
        "school_year": active_year.id,
        "title": "רגשות",
        "description": "שיעור פתיחה",
    }
    resp = client_a.post("/lessons/", payload, format="json")

    assert resp.status_code == 201
    assert resp.data["title"] == "רגשות"
    assert resp.data["assignments"] == []  # nested, empty on a fresh lesson


@pytest.mark.django_db
def test_list_lessons_ordered_newest_first(
    client_a, school_a, counselor_a, active_year
):
    older = _lesson(school_a, counselor_a, active_year, title="ישן")
    _lesson(school_a, counselor_a, active_year, title="חדש")
    # Force a deterministic gap (update bypasses auto_now_add).
    LessonPlan.all_objects.filter(id=older.id).update(
        created_at=timezone.now() - timedelta(days=1)
    )

    resp = client_a.get("/lessons/")
    assert resp.status_code == 200
    assert resp.data["results"][0]["title"] == "חדש"


@pytest.mark.django_db
def test_retrieve_lesson_includes_assignments(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_levels[0], class_number=2
    )

    resp = client_a.get(f"/lessons/{lesson.id}/")
    assert resp.status_code == 200
    assert len(resp.data["assignments"]) == 1
    assert resp.data["assignments"][0]["class_level_name"] == class_levels[0].name


@pytest.mark.django_db
def test_update_lesson_title_persists(client_a, school_a, counselor_a, active_year):
    lesson = _lesson(school_a, counselor_a, active_year, title="ישן")

    resp = client_a.patch(f"/lessons/{lesson.id}/", {"title": "מעודכן"}, format="json")
    assert resp.status_code == 200
    lesson.refresh_from_db()
    assert lesson.title == "מעודכן"


@pytest.mark.django_db
def test_delete_lesson_cascade_soft_deletes_assignments(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    assignment = factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_levels[0]
    )

    resp = client_a.delete(f"/lessons/{lesson.id}/")
    assert resp.status_code == 204
    # Both the lesson and its assignment are soft-deleted (archived), not hard-deleted.
    assert LessonPlan.all_objects.get(id=lesson.id).deleted_at is not None
    assert (
        LessonClassAssignment.all_objects.get(id=assignment.id).deleted_at is not None
    )


# --- calendar action -------------------------------------------------------


@pytest.mark.django_db
def test_calendar_returns_lessons_and_events(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_levels[0], planned_date=timezone.now()
    )
    student = factories.StudentFactory(school=school_a)
    factories.StudentEventFactory(student=student, counselor=counselor_a)

    resp = client_a.get("/lessons/calendar/")
    assert resp.status_code == 200
    assert {item["type"] for item in resp.data} == {"lesson", "student_event"}


@pytest.mark.django_db
def test_calendar_assignment_without_planned_date_is_excluded(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    # planned_date defaults to None -> the assignment is skipped in the calendar.
    factories.LessonClassAssignmentFactory(lesson=lesson, class_level=class_levels[0])

    resp = client_a.get("/lessons/calendar/")
    assert resp.status_code == 200
    assert resp.data == []


@pytest.mark.django_db
def test_calendar_filters_out_of_range(
    client_a, school_a, counselor_a, active_year, class_levels
):
    lesson = _lesson(school_a, counselor_a, active_year)
    factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_levels[0], planned_date=timezone.now()
    )
    student = factories.StudentFactory(school=school_a)
    factories.StudentEventFactory(student=student, counselor=counselor_a)

    future = (timezone.now() + timedelta(days=30)).isoformat()
    # Pass via the data dict so the client URL-encodes the '+' tz offset.
    resp = client_a.get("/lessons/calendar/", {"start": future})
    assert resp.status_code == 200
    assert resp.data == []


@pytest.mark.django_db
def test_calendar_invalid_date_param_returns_500(
    client_a, school_a, counselor_a, active_year, class_levels
):
    """FINDING (latent bug): an unparseable start/end is parsed to None and fed
    straight into ``planned_date__gte=None``, which Django rejects -> unhandled
    500. It should be validated to a 400. Documented here as current behavior."""
    lesson = _lesson(school_a, counselor_a, active_year)
    factories.LessonClassAssignmentFactory(
        lesson=lesson, class_level=class_levels[0], planned_date=timezone.now()
    )

    client_a.raise_request_exception = False
    resp = client_a.get("/lessons/calendar/?start=not-a-date")
    assert resp.status_code == 500
