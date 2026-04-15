from core.repositories.school_year_repository import SchoolYearRepository


class SchoolYearService:

    @staticmethod
    def create_school_year(data):        
        return SchoolYearRepository.create(**data)

    @staticmethod
    def update_school_year(year, data):
        return SchoolYearRepository.update(year, **data)

    @staticmethod
    def delete_school_year(year):
        return SchoolYearRepository.delete(year)