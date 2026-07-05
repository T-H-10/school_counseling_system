from django.db import transaction

from core.models import SchoolYear
from core.services.base import apply_fields, create_excluding


class SchoolYearService:
    @staticmethod
    def create_school_year(data):
        should_activate = bool(data.get("is_active"))
        year = create_excluding(SchoolYear, {**data, "is_active": False})
        if should_activate:
            SchoolYearService.activate_year(year.id)
            year.refresh_from_db()
        return year

    @staticmethod
    def update_school_year(year, data):
        if data.get("is_active"):
            SchoolYearService.activate_year(year.id)
            year.refresh_from_db()
            return year
        return apply_fields(year, data)

    @staticmethod
    @transaction.atomic
    def activate_year(year_id):
        """Atomically deactivate all years then activate the given one.

        Uses transaction.atomic so there is never a moment with zero active years.
        The DB partial unique index (unique_active_school_year) enforces that at
        most one year is active at the database level.
        """
        SchoolYear.objects.all().update(is_active=False)
        updated = SchoolYear.objects.filter(pk=year_id).update(is_active=True)
        if not updated:
            raise SchoolYear.DoesNotExist(f"SchoolYear {year_id} not found")

    @staticmethod
    def delete_school_year(year):
        year.delete()
