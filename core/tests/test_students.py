"""P0 — Student create/update validation.

Covers the two validation layers a student write passes through:
- serializer field validators (name length, ID format, phone format, the
  required-on-create enrollment fields) with their exact (Hebrew) messages, and
- the service-level duplicate-id_number guard (IntegrityError -> 400).

Messages are asserted verbatim because the React UI renders them.
"""
import pytest

from core.models import Student, StudentEnrollment
from core.tests import factories


def _valid_payload(active_year, class_level, drop=(), **overrides):
    """A valid POST /students/ body; ``drop`` removes keys, kwargs override."""
    payload = {
        "full_name": "ישראל ישראלי",
        "id_number": "123456789",
        "school_year": active_year.id,
        "class_level": class_level.id,
        "class_number": 1,
    }
    payload.update(overrides)
    for key in drop:
        payload.pop(key, None)
    return payload


# --- Happy path ------------------------------------------------------------

@pytest.mark.django_db
def test_create_student_succeeds_and_creates_enrollment(client_a, active_year, class_levels):
    payload = _valid_payload(active_year, class_levels[0])
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 201
    assert resp.data["full_name"] == "ישראל ישראלי"
    # The write-only enrollment fields produced an enrollment, reflected back.
    assert resp.data["current_class_level"] == class_levels[0].name
    assert resp.data["current_class_number"] == 1

    student = Student.objects.get(id=resp.data["id"])
    assert StudentEnrollment.objects.filter(student=student, school_year=active_year).count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("id_number", ["12345678", "123456789"])
def test_create_accepts_8_and_9_digit_ids(client_a, active_year, class_levels, id_number):
    payload = _valid_payload(active_year, class_levels[0], id_number=id_number)
    assert client_a.post("/students/", payload, format="json").status_code == 201


@pytest.mark.django_db
def test_update_student_name_persists(client_a, active_year, class_levels):
    created = client_a.post("/students/", _valid_payload(active_year, class_levels[0]), format="json")
    student_id = created.data["id"]

    resp = client_a.patch(f"/students/{student_id}/", {"full_name": "שם מעודכן"}, format="json")
    assert resp.status_code == 200
    assert resp.data["full_name"] == "שם מעודכן"


# --- Field validation ------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("bad_id", ["abcdefghi", "1234567", "12.345678"])
def test_create_invalid_id_number_rejected(client_a, active_year, class_levels, bad_id):
    """Non-digit or wrong-length (but <=9 char) IDs reach validate_id_number."""
    payload = _valid_payload(active_year, class_levels[0], id_number=bad_id)
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert "Invalid ID number" in resp.data["id_number"]


@pytest.mark.django_db
def test_create_id_number_over_9_chars_rejected_by_length(client_a, active_year, class_levels):
    """A 10-digit ID is stopped by the model's max_length=9 (CharField) before the
    custom validator runs — so the code is 'max_length', not 'Invalid ID number'."""
    payload = _valid_payload(active_year, class_levels[0], id_number="1234567890")
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert resp.data["id_number"][0].code == "max_length"


@pytest.mark.django_db
def test_create_short_name_rejected(client_a, active_year, class_levels):
    payload = _valid_payload(active_year, class_levels[0], full_name="א")
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert "Name too short" in resp.data["full_name"]


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["mother_phone", "father_phone"])
def test_create_invalid_phone_rejected(client_a, active_year, class_levels, field):
    payload = _valid_payload(active_year, class_levels[0], **{field: "123"})
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert "Invalid phone number" in resp.data[field]


# --- Required-on-create enrollment fields ----------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("field", ["school_year", "class_level", "class_number"])
def test_create_missing_enrollment_field_rejected(client_a, active_year, class_levels, field):
    payload = _valid_payload(active_year, class_levels[0], drop=[field])
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert "שדה זה הוא חובה" in resp.data[field]


@pytest.mark.django_db
def test_create_class_number_below_one_rejected(client_a, active_year, class_levels):
    payload = _valid_payload(active_year, class_levels[0], class_number=0)
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert "class_number" in resp.data


# --- Duplicate id_number (service-level IntegrityError guard) ---------------

@pytest.mark.django_db
def test_create_duplicate_id_number_same_school_rejected(client_a, school_a, active_year, class_levels):
    """A live duplicate is caught by DRF's auto UniqueValidator (code 'unique')
    at serializer time — the service's custom message is NOT what the API returns
    here (see the soft-delete edge test for where that message actually fires)."""
    factories.StudentFactory(school=school_a, id_number="123456789")
    payload = _valid_payload(active_year, class_levels[0], id_number="123456789")
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert resp.data["id_number"][0].code == "unique"


@pytest.mark.django_db
def test_create_duplicate_id_number_across_schools_rejected(client_a, school_b, active_year, class_levels):
    """id_number is globally unique, so a clash with ANOTHER school's student is
    still rejected (code 'unique')."""
    factories.StudentFactory(school=school_b, id_number="123456789")
    payload = _valid_payload(active_year, class_levels[0], id_number="123456789")
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert resp.data["id_number"][0].code == "unique"


@pytest.mark.django_db
def test_create_duplicate_of_soft_deleted_id_hits_service_message(client_a, school_a, active_year, class_levels):
    """The service's custom Hebrew duplicate message is reachable ONLY here:
    the alive-only manager hides a soft-deleted student from UniqueValidator, so
    validation passes, but the DB unique constraint (spanning soft-deleted rows)
    raises IntegrityError, which the service maps to its custom 400."""
    student = factories.StudentFactory(school=school_a, id_number="123456789")
    student.delete()  # soft-delete: sets deleted_at, row remains in the DB

    payload = _valid_payload(active_year, class_levels[0], id_number="123456789")
    resp = client_a.post("/students/", payload, format="json")

    assert resp.status_code == 400
    assert "תלמיד עם תעודת זהות זו כבר קיים בבית הספר" in resp.data["id_number"]


# --- Update edge: enrollment fields are ignored on update ------------------

@pytest.mark.django_db
def test_update_ignores_enrollment_fields(client_a, active_year, class_levels):
    created = client_a.post("/students/", _valid_payload(active_year, class_levels[0]), format="json")
    student_id = created.data["id"]

    # PATCH carrying enrollment fields must not create a second enrollment.
    resp = client_a.patch(
        f"/students/{student_id}/",
        {"class_number": 9, "class_level": class_levels[1].id},
        format="json",
    )
    assert resp.status_code == 200
    assert StudentEnrollment.objects.filter(student_id=student_id).count() == 1
