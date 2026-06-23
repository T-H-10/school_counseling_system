import django_filters

from core.models import ClassLevel, Student


class StudentFilter(django_filters.FilterSet):
    class_level = django_filters.ModelChoiceFilter(
        queryset=ClassLevel.objects.all(),
        field_name="enrollments__class_level",
        label="שכבה",
    )
    class_number = django_filters.NumberFilter(
        field_name="enrollments__class_number",
        lookup_expr="exact",
        label="מספר כיתה",
    )

    class Meta:
        model = Student
        fields = ["class_level", "class_number"]
