"""P0 — Global header search: per-category matching, school-scoping, edge cases."""

import pytest

from core.tests import factories


@pytest.mark.django_db
def test_students_category_matches_by_name(client_a, school_a):
    factories.StudentFactory(school=school_a, full_name="דנה כהן")
    factories.StudentFactory(school=school_a, full_name="יוסי לוי")

    resp = client_a.get("/search/?q=דנה")
    assert resp.status_code == 200
    assert [s["full_name"] for s in resp.data["students"]] == ["דנה כהן"]


@pytest.mark.django_db
def test_students_category_matches_by_id_number(client_a, school_a):
    student = factories.StudentFactory(school=school_a)

    resp = client_a.get(f"/search/?q={student.id_number[:5]}")
    assert resp.status_code == 200
    assert student.id in [s["id"] for s in resp.data["students"]]


@pytest.mark.django_db
def test_documents_category_matches_by_title(client_a, school_a, counselor_a):
    factories.DocumentFactory(school=school_a, counselor=counselor_a, title="דוח מיוחד")
    factories.DocumentFactory(school=school_a, counselor=counselor_a, title="אחר")

    resp = client_a.get("/search/?q=מיוחד")
    assert resp.status_code == 200
    assert [d["title"] for d in resp.data["documents"]] == ["דוח מיוחד"]


@pytest.mark.django_db
def test_lessons_category_matches_by_title(client_a, school_a, counselor_a):
    factories.LessonPlanFactory(school=school_a, counselor=counselor_a, title="מניעת אלימות")
    factories.LessonPlanFactory(school=school_a, counselor=counselor_a, title="אחר")

    resp = client_a.get("/search/?q=אלימות")
    assert resp.status_code == 200
    assert [l["title"] for l in resp.data["lessons"]] == ["מניעת אלימות"]


@pytest.mark.django_db
def test_classes_category_matches_by_level_name(client_a, school_a, active_year):
    factories.StudentEnrollmentFactory(
        student=factories.StudentFactory(school=school_a),
        school=school_a,
        school_year=active_year,
        class_level=factories.ClassLevelFactory(name="ג"),
        class_number=2,
    )

    resp = client_a.get("/search/?q=ג")
    assert resp.status_code == 200
    assert resp.data["classes"] == [
        {"class_level": factories.ClassLevel.objects.get(name="ג").id, "class_level_name": "ג", "class_number": 2}
    ]


@pytest.mark.django_db
def test_classes_category_matches_by_class_number(client_a, school_a, active_year):
    factories.StudentEnrollmentFactory(
        student=factories.StudentFactory(school=school_a),
        school=school_a,
        school_year=active_year,
        class_level=factories.ClassLevelFactory(name="ד"),
        class_number=3,
    )

    resp = client_a.get("/search/?q=3")
    assert resp.status_code == 200
    assert len(resp.data["classes"]) == 1
    assert resp.data["classes"][0]["class_number"] == 3


@pytest.mark.django_db
def test_blank_query_returns_all_empty(client_a, school_a):
    factories.StudentFactory(school=school_a, full_name="דנה")

    resp = client_a.get("/search/?q=   ")
    assert resp.status_code == 200
    assert resp.data == {"students": [], "classes": [], "documents": [], "lessons": []}


@pytest.mark.django_db
def test_single_char_query_matches_class_level(client_a, school_a, active_year):
    factories.StudentEnrollmentFactory(
        student=factories.StudentFactory(school=school_a),
        school=school_a,
        school_year=active_year,
        class_level=factories.ClassLevelFactory(name="ה"),
        class_number=1,
    )

    resp = client_a.get("/search/?q=ה")
    assert resp.status_code == 200
    assert resp.data["classes"] == [
        {
            "class_level": factories.ClassLevel.objects.get(name="ה").id,
            "class_level_name": "ה",
            "class_number": 1,
        }
    ]


@pytest.mark.django_db
def test_missing_query_param_does_not_error(client_a):
    resp = client_a.get("/search/")
    assert resp.status_code == 200
    assert resp.data == {"students": [], "classes": [], "documents": [], "lessons": []}


@pytest.mark.django_db
def test_results_are_scoped_to_own_school(client_a, school_a, school_b, counselor_b):
    factories.StudentFactory(school=school_b, full_name="תלמיד בית ספר ב")
    factories.DocumentFactory(school=school_b, counselor=counselor_b, title="מסמך בית ספר ב")
    factories.LessonPlanFactory(school=school_b, counselor=counselor_b, title="שיעור בית ספר ב")

    resp = client_a.get("/search/?q=בית ספר ב")
    assert resp.status_code == 200
    assert resp.data["students"] == []
    assert resp.data["documents"] == []
    assert resp.data["lessons"] == []


@pytest.mark.django_db
def test_requires_authentication(api):
    resp = api.get("/search/?q=test")
    assert resp.status_code == 401
