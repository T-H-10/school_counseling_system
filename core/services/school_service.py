
from core.models import School


class SchoolService:

    @staticmethod
    def create_school(data):
        return School.objects.create(**data)

    @staticmethod
    def update_school(school, data):

        for attr, value in data.items():
            setattr(school, attr, value)
        school.save()
        return school

    @staticmethod
    def delete_school(school):
        
        school.delete()