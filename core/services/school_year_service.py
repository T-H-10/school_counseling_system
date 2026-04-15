from core.models import SchoolYear


class SchoolYearService:

    @staticmethod
    def create_school_year(data):        
        clean_data = {
            k: v for k, v in data.items()
            if k != "id"
        }
        return SchoolYear.objects.create(**clean_data)

    @staticmethod
    def update_school_year(year, data):
        clean_data = {
            k: v for k, v in data.items()
            if k != "id"
        }
        
        for attr, value in clean_data.items():
            setattr(year, attr, value)
        year.save()
        return year

    @staticmethod
    def delete_school_year(year):
        year.delete()