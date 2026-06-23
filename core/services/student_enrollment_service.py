from core.helpers import ensure_same_school
from core.models import ClassLevel, SchoolYear, StudentEnrollment
from core.services.base import apply_fields
from django.db.models import Count, Max


class StudentEnrollmentService:
    @staticmethod
    def create_enrollment(user, data):
        school = user.counselor.school
        student = data["student"]
        ensure_same_school(user, student)
        return StudentEnrollment.objects.create(
            student=student,
            school_year=data["school_year"],
            class_level=data.get("class_level"),
            class_number=data["class_number"],
            teacher_name=data.get("teacher_name", ""),
            school=school,
        )

    @staticmethod
    def update_enrollment(user, enrollment, data):
        ensure_same_school(user, enrollment)
        return apply_fields(enrollment, data, exclude={"school", "student", "school_year", "id"})

    @staticmethod
    def delete_enrollment(user, enrollment):
        ensure_same_school(user, enrollment)
        enrollment.delete()

    @staticmethod
    def get_classes(user):
        school = user.counselor.school
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return []
        groups = (
            StudentEnrollment.objects.filter(school=school, school_year=active_year)
            .values(
                "class_level",
                "class_level__name",
                "class_number",
                "school_year",
                "school_year__name",
            )
            .annotate(
                student_count=Count("pk"),
                teacher_name=Max("teacher_name"),
            )
            .order_by("class_level__name", "class_number")
        )
        return list(groups)

    @staticmethod
    def set_class_teacher(user, data):
        school = user.counselor.school
        updated = StudentEnrollment.objects.filter(
            school=school,
            school_year_id=data["school_year"],
            class_level_id=data["class_level"],
            class_number=data["class_number"],
        ).update(teacher_name=data.get("teacher_name", ""))
        return updated

    @staticmethod
    def promote_students(user, data):
        school = user.counselor.school
        from_year = SchoolYear.objects.get(pk=data["from_year"])
        to_year = SchoolYear.objects.get(pk=data["to_year"])

        levels = list(ClassLevel.objects.all().order_by("name"))
        next_level_map = {levels[i].id: levels[i + 1] for i in range(len(levels) - 1)}

        enrollments = StudentEnrollment.objects.filter(
            school=school, school_year=from_year
        ).select_related("class_level", "student")

        already_enrolled = set(
            StudentEnrollment.objects.filter(school=school, school_year=to_year).values_list(
                "student_id", flat=True
            )
        )

        created = 0
        skipped = 0
        for enrollment in enrollments:
            if enrollment.student_id in already_enrolled:
                skipped += 1
                continue
            next_level = (
                next_level_map.get(enrollment.class_level_id) if enrollment.class_level_id else None
            )
            if next_level is None:
                skipped += 1
                continue
            StudentEnrollment.objects.create(
                student=enrollment.student,
                school_year=to_year,
                class_level=next_level,
                class_number=enrollment.class_number,
                teacher_name="",
                school=school,
            )
            created += 1

        return {"created": created, "skipped": skipped}
