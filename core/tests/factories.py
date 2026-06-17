"""factory_boy factories for the API test suite.

Factories produce valid-by-default objects; each test overrides only the one
field under test. Sub-factories wire the FK graph, and ``Sequence`` keeps the
unique fields (``id_number``, ``institution_code``, ``username``) collision-free.
``school`` on child rows is pinned to the parent's school via ``SelfAttribute``
so objects are internally consistent (same-tenant) unless a test says otherwise.
"""
import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from core.models import (
    ClassLevel,
    Counselor,
    LessonClassAssignment,
    LessonPlan,
    School,
    SchoolYear,
    Student,
    StudentEnrollment,
    StudentEvent,
)

# Shared password for every factory-built user, so tests can log in via /token/.
DEFAULT_PASSWORD = "test-pass-12345"

# The eight grade levels, in order (א..ח).
GRADE_LEVELS = "אבגדהוזח"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    # Store the hash directly (no post-generation save) so /token/ login works.
    password = factory.LazyFunction(lambda: make_password(DEFAULT_PASSWORD))


class AdminUserFactory(UserFactory):
    username = factory.Sequence(lambda n: f"admin{n}")
    is_staff = True
    is_superuser = True


class SchoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = School

    name = factory.Sequence(lambda n: f"בית ספר {n}")
    institution_code = factory.Sequence(lambda n: str(100000 + n))


class CounselorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Counselor

    user = factory.SubFactory(UserFactory)
    school = factory.SubFactory(SchoolFactory)
    full_name = factory.Sequence(lambda n: f"יועץ {n}")


class ClassLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassLevel
        django_get_or_create = ("name",)

    name = "א"


class SchoolYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SchoolYear
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"{2025 + n}-{2026 + n}")
    is_active = False


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    school = factory.SubFactory(SchoolFactory)
    full_name = factory.Sequence(lambda n: f"תלמיד {n}")
    # 9 digits — valid for validate_id_number and unique.
    id_number = factory.Sequence(lambda n: str(300000000 + n))


class StudentEnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentEnrollment

    student = factory.SubFactory(StudentFactory)
    school_year = factory.SubFactory(SchoolYearFactory)
    school = factory.SelfAttribute("student.school")
    class_level = factory.SubFactory(ClassLevelFactory)
    class_number = 1
    teacher_name = ""


class StudentEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentEvent

    student = factory.SubFactory(StudentFactory)
    counselor = factory.SubFactory(CounselorFactory)
    school = factory.SelfAttribute("student.school")
    event_type = "meeting"
    title = factory.Sequence(lambda n: f"אירוע {n}")
    status = "pending"


class LessonPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LessonPlan

    school = factory.SubFactory(SchoolFactory)
    counselor = factory.SubFactory(CounselorFactory, school=factory.SelfAttribute("..school"))
    school_year = factory.SubFactory(SchoolYearFactory)
    title = factory.Sequence(lambda n: f"מערך {n}")


class LessonClassAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LessonClassAssignment

    lesson = factory.SubFactory(LessonPlanFactory)
    school = factory.SelfAttribute("lesson.school")
    class_level = factory.SubFactory(ClassLevelFactory)
    class_number = 1
    status = "planned"
