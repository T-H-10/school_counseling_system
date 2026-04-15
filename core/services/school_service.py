
from core.models import School


class SchoolService:

    @staticmethod
    def create_school(data):
        clean_data = {
            k: v for k, v in data.items()
            if k != "id"
        }

        return School.objects.create(**clean_data)

    @staticmethod
    def update_school(school, data):

        clean_data = {
            k: v for k, v in data.items()
            if k != "id"
        }

        for attr, value in clean_data.items():
            setattr(school, attr, value)
        school.save()
        return school

    @staticmethod
    def delete_school(school):
        school.delete()