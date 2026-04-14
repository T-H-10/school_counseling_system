from core.repositories.school_year_repository import SchoolYearRepository


class SchoolYearService:

    @staticmethod
    def create_school_year(data):
        return SchoolYearRepository.create(**data)

    @staticmethod
    def update_school_year(year_id, data):
        year = SchoolYearRepository.get_by_id(year_id)
        return SchoolYearRepository.update(year, data)

    @staticmethod
    def delete_school_year(year_id):
        year = SchoolYearRepository.get_by_id(year_id)
        return SchoolYearRepository.delete(year)