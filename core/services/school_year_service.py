from core.models import SchoolYear
from core.services.base import apply_fields, create_excluding


class SchoolYearService:
    @staticmethod
    def create_school_year(data):
        return create_excluding(SchoolYear, data)

    @staticmethod
    def update_school_year(year, data):
        return apply_fields(year, data)

    @staticmethod
    def delete_school_year(year):
        year.delete()
