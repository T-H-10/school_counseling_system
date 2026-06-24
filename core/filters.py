import django_filters

from core.models import ClassLevel, SchoolYear, Student, StudentEnrollment


class StudentFilter(django_filters.FilterSet):
    class_level = django_filters.ModelChoiceFilter(
        queryset=ClassLevel.objects.all(),
        method="filter_class_level",
        label="שכבה",
    )
    class_number = django_filters.NumberFilter(
        method="filter_class_number",
        label="מספר כיתה",
    )
    inactive = django_filters.BooleanFilter(method="filter_inactive", label="לא פעיל")

    def _active_year_enrollment_sub(self, **filters):
        school = self.request.user.counselor.school
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return StudentEnrollment.objects.none().values("student_id")
        return StudentEnrollment.objects.filter(
            school=school, school_year=active_year, **filters
        ).values("student_id")

    def filter_class_level(self, queryset, name, value):
        return queryset.filter(id__in=self._active_year_enrollment_sub(class_level=value))

    def filter_class_number(self, queryset, name, value):
        return queryset.filter(id__in=self._active_year_enrollment_sub(class_number=value))

    def filter_inactive(self, queryset, name, value):
        """Filter by enrollment status relative to the active school year.

        inactive=true  → students with no enrollment in the active year
                         (graduated, withdrew, transferred, never promoted).
                         All such students appear together without further
                         categorisation.
        inactive=false → students enrolled in the active year.

        If no active year exists every student is treated as inactive:
        inactive=true returns all students; inactive=false returns none.
        """
        school = self.request.user.counselor.school
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return queryset if value else queryset.none()
        enrolled_ids = StudentEnrollment.objects.filter(
            school=school, school_year=active_year
        ).values_list("student_id", flat=True)
        if value:
            return queryset.exclude(id__in=enrolled_ids)
        return queryset.filter(id__in=enrolled_ids)

    class Meta:
        model = Student
        fields = ["class_level", "class_number", "inactive"]
