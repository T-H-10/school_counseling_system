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
    assert StudentEnrollment.objects.filter(student=student, school_year=active_year).count() == 1


@pytest.mark.django_db
def test_list_enrollments_filtered_by_student(client_a, school_a, active_year, class_levels):
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
def test_set_class_teacher_updates_matching_rows(client_a, school_a, active_year, class_levels):
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
def test_set_class_teacher_missing_field_rejected(client_a, active_year, class_levels, missing):
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
    assert resp.data["created"] == 1
    assert resp.data["skipped"] == 0
    assert resp.data["skipped_students"] == []
    promoted = StudentEnrollment.objects.get(student=enrollment.student, school_year=next_year)
    assert promoted.class_level.name == class_levels[1].name  # grade ב


@pytest.mark.django_db
def test_promote_skips_top_grade(client_a, school_a, active_year, class_levels):
    enrollment = _enroll(school_a, active_year, class_levels[-1])  # grade ח, no next level
    next_year = factories.SchoolYearFactory(name="2026-2027")

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["created"] == 0
    assert resp.data["skipped"] == 1
    assert len(resp.data["skipped_students"]) == 1
    skipped = resp.data["skipped_students"][0]
    assert skipped["id"] == enrollment.student_id
    assert skipped["grade"] == class_levels[-1].name
    assert skipped["reason"] == "last_grade"


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
    assert resp.data["created"] == 0
    assert resp.data["skipped"] == 1
    skipped = resp.data["skipped_students"][0]
    assert skipped["reason"] == "already_enrolled"


@pytest.mark.django_db
def test_promote_missing_year_rejected(client_a, active_year):
    resp = client_a.post("/enrollments/promote/", {"from_year": active_year.id}, format="json")
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
def test_duplicate_enrollment_same_year_rejected(client_a, school_a, active_year, class_levels):
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


# --- promote: edge cases ---------------------------------------------------


@pytest.mark.django_db
def test_promote_zero_students_rejected(client_a, active_year):
    """Promoting from a year with no enrollments is rejected with 400."""
    next_year = factories.SchoolYearFactory(name="2026-2027")

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 400
    assert "שנת המקור אינה מכילה תלמידים" in resp.data["error"]


@pytest.mark.django_db
def test_promote_all_last_grade(client_a, school_a, active_year, class_levels):
    """All students in כיתה ח' → created=0, all skipped with reason last_grade."""
    for _ in range(3):
        _enroll(school_a, active_year, class_levels[-1])  # grade ח
    next_year = factories.SchoolYearFactory(name="2026-2027")

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["created"] == 0
    assert resp.data["skipped"] == 3
    assert all(s["reason"] == "last_grade" for s in resp.data["skipped_students"])


@pytest.mark.django_db
def test_promote_idempotent(client_a, school_a, active_year, class_levels):
    """Running promote twice is idempotent: second run creates nothing."""
    _enroll(school_a, active_year, class_levels[0])
    next_year = factories.SchoolYearFactory(name="2026-2027")
    payload = {"from_year": active_year.id, "to_year": next_year.id}

    resp1 = client_a.post("/enrollments/promote/", payload, format="json")
    assert resp1.data["created"] == 1

    resp2 = client_a.post("/enrollments/promote/", payload, format="json")
    assert resp2.status_code == 200
    assert resp2.data["created"] == 0
    assert resp2.data["skipped"] == 1
    assert resp2.data["skipped_students"][0]["reason"] == "already_enrolled"
    # DB must still have exactly one enrollment in the target year.
    assert StudentEnrollment.objects.filter(school_year=next_year).count() == 1


@pytest.mark.django_db
def test_promote_skipped_students_include_grade(client_a, school_a, active_year, class_levels):
    """Skipped students carry the grade name so the UI can display it."""
    _enroll(school_a, active_year, class_levels[-1])  # ח
    next_year = factories.SchoolYearFactory(name="2026-2027")

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    skipped = resp.data["skipped_students"][0]
    assert "grade" in skipped
    assert skipped["grade"] == "ח"
    assert "full_name" in skipped


# --- inactive student filter -----------------------------------------------


@pytest.mark.django_db
def test_inactive_filter_returns_unenrolled_students(client_a, school_a, active_year, class_levels):
    """?inactive=true returns students with no enrollment in the active year."""
    enrolled_student = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=enrolled_student, school_year=active_year, class_level=class_levels[0], school=school_a
    )
    inactive_student = factories.StudentFactory(school=school_a)  # no enrollment

    resp = client_a.get("/students/?inactive=true")
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.data["results"]]
    assert inactive_student.id in ids
    assert enrolled_student.id not in ids


@pytest.mark.django_db
def test_inactive_false_returns_enrolled_students(client_a, school_a, active_year, class_levels):
    """?inactive=false returns only students enrolled in the active year."""
    enrolled = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=enrolled, school_year=active_year, class_level=class_levels[0], school=school_a
    )
    factories.StudentFactory(school=school_a)  # unenrolled

    resp = client_a.get("/students/?inactive=false")
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.data["results"]]
    assert enrolled.id in ids
    assert len(ids) == 1


@pytest.mark.django_db
def test_inactive_filter_no_active_year(client_a, school_a):
    """When no active year exists, inactive=true returns all students."""
    factories.StudentFactory(school=school_a)
    factories.StudentFactory(school=school_a)

    resp = client_a.get("/students/?inactive=true")
    assert resp.status_code == 200
    assert resp.data["count"] == 2


# --- activate_year -----------------------------------------------------------


@pytest.mark.django_db
def test_activate_year_deactivates_others(admin_client, active_year):
    """PATCH is_active=True on a year atomically deactivates all other years."""
    new_year = factories.SchoolYearFactory(name="2026-2027", is_active=False)

    resp = admin_client.patch(f"/schoolYears/{new_year.id}/", {"is_active": True}, format="json")
    assert resp.status_code == 200

    from core.models import SchoolYear as SY
    active_years = SY.objects.filter(is_active=True)
    assert active_years.count() == 1
    assert active_years.first().id == new_year.id


@pytest.mark.django_db
def test_create_active_year_deactivates_others(admin_client, active_year):
    """POST is_active=True on a new year atomically deactivates all other years."""
    resp = admin_client.post(
        "/schoolYears/", {"name": "2026-2027", "is_active": True}, format="json"
    )
    assert resp.status_code == 201

    from core.models import SchoolYear as SY
    active_years = SY.objects.filter(is_active=True)
    assert active_years.count() == 1
    assert active_years.first().id == resp.data["id"]
    assert active_years.first().id != active_year.id


@pytest.mark.django_db
def test_db_constraint_rejects_two_active_years(db):
    """The DB partial unique index prevents two rows with is_active=True."""
    from django.db import IntegrityError

    factories.SchoolYearFactory(name="2025-2026", is_active=True)
    with pytest.raises(IntegrityError):
        factories.SchoolYearFactory(name="2026-2027", is_active=True)


@pytest.mark.django_db
def test_promote_same_year_rejected(client_a, school_a, active_year, class_levels):
    """Promoting from a year to itself is rejected with 400."""
    _enroll(school_a, active_year, class_levels[0])

    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": active_year.id},
        format="json",
    )
    assert resp.status_code == 400
    assert "שונות" in resp.data["error"]


# --- enrollment history: serializer fields ---------------------------------


@pytest.mark.django_db
def test_enrollment_list_includes_name_fields(client_a, school_a, active_year, class_levels):
    """GET /enrollments/?student={id} includes school_year_name and class_level_name."""
    enrollment = _enroll(school_a, active_year, class_levels[2])  # grade ג

    resp = client_a.get(f"/enrollments/?student={enrollment.student_id}")
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    row = resp.data["results"][0]
    assert row["school_year_name"] == active_year.name
    assert row["class_level_name"] == class_levels[2].name


@pytest.mark.django_db
def test_enrollment_list_ordered_newest_first(client_a, school_a, active_year, class_levels):
    """GET /enrollments/?student={id} returns rows ordered newest school year first."""
    student = factories.StudentFactory(school=school_a)
    older_year = factories.SchoolYearFactory(name="2023-2024")  # alphabetically earlier
    factories.StudentEnrollmentFactory(
        student=student, school_year=older_year, class_level=class_levels[0], school=school_a
    )
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[1], school=school_a
    )

    resp = client_a.get(f"/enrollments/?student={student.id}")
    assert resp.status_code == 200
    names = [r["school_year_name"] for r in resp.data["results"]]
    assert names[0] == active_year.name   # "2025-2026" comes first (newest)
    assert names[1] == older_year.name    # "2023-2024" comes second


# --- Bug fixes: cross-year filter isolation --------------------------------


@pytest.mark.django_db
def test_class_level_filter_scoped_to_active_year(client_a, school_a, active_year, class_levels):
    """A student promoted out of ז must not appear when filtering ז in the active year."""
    past_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=student, school_year=past_year, class_level=class_levels[6],  # ז
        class_number=1, school=school_a,
    )
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[7],  # ח
        class_number=1, school=school_a,
    )

    resp = client_a.get(f"/students/?class_level={class_levels[6].id}&class_number=1")
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.data["results"]]
    assert student.id not in ids


@pytest.mark.django_db
def test_class_number_filter_scoped_to_active_year(client_a, school_a, active_year, class_levels):
    """Filtering by class_number returns only students in that number in the active year."""
    past_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=student, school_year=past_year, class_level=class_levels[0],
        class_number=2, school=school_a,
    )
    factories.StudentEnrollmentFactory(
        student=student, school_year=active_year, class_level=class_levels[0],
        class_number=1, school=school_a,
    )

    resp = client_a.get("/students/?class_number=2")
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.data["results"]]
    assert student.id not in ids


@pytest.mark.django_db
def test_class_filter_no_active_year_returns_empty(client_a, school_a, class_levels):
    """When no active year exists, class_level filter must return an empty list."""
    factories.StudentFactory(school=school_a)  # unenrolled student, no active year

    resp = client_a.get(f"/students/?class_level={class_levels[0].id}")
    assert resp.status_code == 200
    assert resp.data["count"] == 0


# --- Bug fixes: soft-deleted students excluded from counts and promotion ----


@pytest.mark.django_db
def test_get_classes_excludes_soft_deleted_students(client_a, school_a, active_year, class_levels):
    """classes/ student_count must not include students who were soft-deleted."""
    _enroll(school_a, active_year, class_levels[0], class_number=1)
    deleted_enrollment = _enroll(school_a, active_year, class_levels[0], class_number=1)
    deleted_enrollment.student.delete()  # soft-delete the student; enrollment row stays

    resp = client_a.get("/enrollments/classes/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["student_count"] == 1


@pytest.mark.django_db
def test_promote_skips_soft_deleted_students(client_a, school_a, active_year, class_levels):
    """Soft-deleted students must not be promoted to the next year."""
    alive_enrollment = _enroll(school_a, active_year, class_levels[0])
    deleted_enrollment = _enroll(school_a, active_year, class_levels[0])
    deleted_enrollment.student.delete()

    next_year = factories.SchoolYearFactory(name="2026-2027")
    resp = client_a.post(
        "/enrollments/promote/",
        {"from_year": active_year.id, "to_year": next_year.id},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["created"] == 1
    assert StudentEnrollment.objects.filter(
        school_year=next_year, student=alive_enrollment.student
    ).exists()
    assert not StudentEnrollment.objects.filter(
        school_year=next_year, student_id=deleted_enrollment.student_id
    ).exists()


# --- is_graduated field ----------------------------------------------------


@pytest.mark.django_db
def test_is_graduated_true_for_last_grade_student(client_a, school_a, active_year, class_levels):
    """A student whose last enrollment was grade ח with no active-year enrollment is graduated."""
    past_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=student, school_year=past_year, class_level=class_levels[-1],  # ח
        class_number=1, school=school_a,
    )

    resp = client_a.get(f"/students/{student.id}/")
    assert resp.status_code == 200
    assert resp.data["is_graduated"] is True


@pytest.mark.django_db
def test_is_graduated_false_for_currently_enrolled_student(
    client_a, school_a, active_year, class_levels
):
    """A student enrolled in the active year is not graduated."""
    enrollment = _enroll(school_a, active_year, class_levels[-1])

    resp = client_a.get(f"/students/{enrollment.student_id}/")
    assert resp.status_code == 200
    assert resp.data["is_graduated"] is False


@pytest.mark.django_db
def test_is_graduated_false_for_transferred_student(client_a, school_a, active_year, class_levels):
    """A student with no active enrollment whose last grade is not ח is not graduated."""
    past_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=student, school_year=past_year, class_level=class_levels[5],  # ו
        class_number=1, school=school_a,
    )

    resp = client_a.get(f"/students/{student.id}/")
    assert resp.status_code == 200
    assert resp.data["is_graduated"] is False


@pytest.mark.django_db
def test_graduation_year_returned_for_last_grade_student(client_a, school_a, active_year, class_levels):
    """graduation_year returns the school year name for a student who finished grade ח."""
    past_year = factories.SchoolYearFactory(name="2024-2025")
    student = factories.StudentFactory(school=school_a)
    factories.StudentEnrollmentFactory(
        student=student, school_year=past_year, class_level=class_levels[-1],  # ח
        class_number=1, school=school_a,
    )

    resp = client_a.get(f"/students/{student.id}/")
    assert resp.status_code == 200
    assert resp.data["graduation_year"] == "2024-2025"
