from core.models import SchoolYear


class SchoolYearService:

    @staticmethod
    def create_school_year(data):        
        return SchoolYear.objects.create(**data)

    @staticmethod
    def update_school_year(year, data):
        for attr, value in data.items():
            setattr(year, attr, value)
        year.save()
        return year

    @staticmethod
    def delete_school_year(year):
        year.delete()