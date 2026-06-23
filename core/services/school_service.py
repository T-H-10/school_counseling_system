from core.models import School
from core.services.base import apply_fields, create_excluding


class SchoolService:
    @staticmethod
    def create_school(data):
        return create_excluding(School, data)

    @staticmethod
    def update_school(school, data):
        return apply_fields(school, data)

    @staticmethod
    def delete_school(school):
        school.delete()
