"""P1 — Enrollments: CRUD, the classes/set-class-teacher/promote actions, and
cross-school + uniqueness negatives.
"""

import pytest

from core.models import StudentEnrollment
from core.tests import factories


def _enroll(school, year, level, class_number=3, teacher=""):
    """Create one student + enrollment in ``school`` for ``year``/``level``."""
    student = factories.StudentFactory(school=school)
    return factories.StudentEnrollmentFactory(
        student=student,
        school_year=year,
        class_level=level,
        class_number=class_number,
        teacher_name=teacher,
    )


# --- CRUD ------------------------------------------------------------------


@pytest.mark.django_db
def test_create_enrollment_succeeds(client_a, school_a, active_year, class_levels):
    student = factories.StudentFactory(school=school_a)
    payload = {
        "student": student.id,
        "school_year": active_year.id,
        "class_level": class_levels[0].id,
        "class_number": 4,
        "teacher_name": "מחנכת א",
    }
    resp = client_a.post("/enrollments/", payload, format="json")

    assert resp.status_code == 201
    assert resp.data["class_number"] == 4
    assert (
        StudentEnrollment.objects.filter(
            student=student, school_year=active_year
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_list_enrollments_filtered_by_student(
    client_a, school_a, active_year, class_levels
):
    enrollment = _enroll(school_a, active_year, class_levels[0])
    _enroll(school_a, active_year, class_levels[1])  # a second, unrelated enrollment

    resp = client_a.get(f"/enrollments/?student={enrollment.student_id}")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["id"] == enrollment.id


@pytest.mark.django_db
def test_update_enrollment_persists(client_a, school_a, active_year, class_levels):
    enrollment = _enroll(school_a, active_year, class_levels[0])

    resp = client_a.patch(
        f"/enrollments/{enrollment.id}/",
        {"class_number": 7, "teacher_name": "מחנך חדש"},
        format="json",
    )
    assert resp.status_code == 200
    enrollment.refresh_from_db()
    assert enrollment.class_number == 7
    assert enrollment.teacher_name == "מחנך חדש"


@pytest.mark.django_db
def test_delete_enrollment_soft_deletes(client_a, school_a, active_year, class_levels):
    enrollment = _enroll(school_a, active_year, class_levels[0])

    resp = client_a.delete(f"/enrollments/{enrollment.id}/")
    assert resp.status_code == 204
    assert client_a.get("/enrollments/").data["count"] == 0
    # Soft-delete: the row remains but is hidden by the default manager.
    assert StudentEnrollment.all_objects.filter(id=enrollment.id).exists()


# --- classes action --------------------------------------------------------


@pytest.mark.django_db
def test_classes_returns_grouped_counts(client_a, school_a, active_year, class_levels):
    _enroll(school_a, active_year, class_levels[0], class_number=3, teacher="מחנכת")
    _enroll(school_a, active_year, class_levels[0], class_number=3, teacher="מחנכת")

    resp = client_a.get("/enrollments/classes/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    group = resp.data[0]
    assert group["student_count"] == 2
    assert group["class_level__name"] == class_levels[0].name
    assert group["teacher_name"] == "מחנכת"


@pytest.mark.django_db
def test_classes_empty_without_active_year(client_a, school_a, class_levels):
    """No active SchoolYear -> the action returns an empty list (not an error)."""
    resp = client_a.get("/enrollments/classes/")
    assert resp.status_code == 200
    assert resp.data == []


# --- set-class-teacher action ---------------------------------------------


@pytest.mark.django_db
def test_set_class_teacher_updates_matching_rows(
    client_a, school_a, active_year, class_levels
):
    _enroll(school_a, active_year, class_levels[0], class_number=3)
    _enroll(school_a, active_year, class_levels[0], class_number=3)

    resp = client_a.post(
        "/enrollments/set-class-teacher/",
        {
            "school_year": active_year.id,
            "class_level": class_levels[0].id,
            "class_number": 3,
            "teacher_name": "המחנכת",
        },
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["updated"] == 2
    assert StudentEnrollment.objects.filter(teacher_name="המחנכת").count() == 2


@pytest.mark.django_db
@pytest.mark.parametrize("missing", ["school_year", "class_level", "class_number"])
def test_set_class_teacher_missing_field_rejected(
    client_a, active_year, class_levels, missing
):
    body = {
        "school_year": active_year.id,
        "class_level": class_levels[0].id,
        "class_number": 3,
    }
    body.pop(missing)
    resp = client_a.post("/enrollments/set-class-teacher/", body, format="json")

    assert resp.status_code == 400
    assert "שדות חסרים" in resp.data["error"]


# --- promote action --------------------------------------------------------


@pytest.mark.django_db
def test_promote_advances_to_next_grade(client_a, school_a, active_year, class_levels):
    enrollment = _enroll(school_a, active_year, class_levels[0])  # grade א
    next_year = factories.SchoolYearFactory(name="2026-2027")

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data == {"created": 1, "skipped": 0}
    promoted = StudentEnrollment.objects.get(
        student=enrollment.student, school_year=next_year
    )
    assert promoted.class_level.name == class_levels[1].name  # grade ב


@pytest.mark.django_db
def test_promote_skips_top_grade(client_a, school_a, active_year, class_levels):
    _enroll(school_a, active_year, class_levels[-1])  # grade ח, no next level
    next_year = factories.SchoolYearFactory(name="2026-2027")

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data == {"created": 0, "skipped": 1}


@pytest.mark.django_db
def test_promote_skips_students_already_in_target_year(
    client_a, school_a, active_year, class_levels
):
    enrollment = _enroll(school_a, active_year, class_levels[0])
    next_year = factories.SchoolYearFactory(name="2026-2027")
    # Same student already enrolled in the target year.
    factories.StudentEnrollmentFactory(
        student=enrollment.student, school_year=next_year, class_level=class_levels[1]
    )

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data == {"created": 0, "skipped": 1}


@pytest.mark.django_db
def test_promote_missing_year_rejected(client_a, active_year):
    resp = client_a.post(
        "/enrollments/promote/", {"from_year": active_year.id}, format="json"
    )
    assert resp.status_code == 400
    assert "נדרשים from_year ו-to_year" in resp.data["error"]


@pytest.mark.django_db
def test_promote_nonexistent_year_rejected(client_a):
    resp = client_a.post(
        "/enrollments/promote/", {"from_year": 99999, "to_year": 88888}, format="json"
    )
    assert resp.status_code == 400
    assert "שנת לימודים לא נמצאה" in resp.data["error"]


# --- Negatives: cross-school + uniqueness ----------------------------------


@pytest.mark.django_db
def test_create_enrollment_for_other_school_student_rejected(
    client_a, school_b, active_year, class_levels
):
    other_student = factories.StudentFactory(school=school_b)
    payload = {
        "student": other_student.id,
        "school_year": active_year.id,
        "class_level": class_levels[0].id,
        "class_number": 1,
    }
    resp = client_a.post("/enrollments/", payload, format="json")

    assert resp.status_code == 400
    assert "Student must belong to your school" in resp.data["non_field_errors"]


@pytest.mark.django_db
def test_duplicate_enrollment_same_year_rejected(
    client_a, school_a, active_year, class_levels
):
    """UNIQUE(student, school_year): a second live enrollment for the same pair
    is rejected with 400 (code 'unique')."""
    enrollment = _enroll(school_a, active_year, class_levels[0])
    payload = {
        "student": enrollment.student_id,
        "school_year": active_year.id,
        "class_level": class_levels[1].id,
        "class_number": 2,
    }
    resp = client_a.post("/enrollments/", payload, format="json")

    assert resp.status_code == 400
    assert resp.data["non_field_errors"][0].code == "unique"
