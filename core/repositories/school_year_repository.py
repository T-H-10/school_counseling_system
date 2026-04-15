from core.models import SchoolYear


class SchoolYearRepository:

    @staticmethod
    def create(**data):
        return SchoolYear.objects.create(**data)

    @staticmethod
    def get_by_id(year_id):
        return SchoolYear.objects.filter(id=year_id).first()
    
    @staticmethod
    def get_all():
        return SchoolYear.objects.all()

    @staticmethod
    def update(year, **data):
        for attr, value in data.items():
            setattr(year, attr, value)
        year.save()
        return year

    @staticmethod
    def delete(year):
        year.delete()