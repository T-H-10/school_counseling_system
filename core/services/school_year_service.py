from core.repositories.school_year_repository import SchoolYearRepository


class SchoolYearService:

    @staticmethod
    def create_school_year(request_user, data):
        if not request_user.is_superuser:
            raise PermissionError("Only admin can create school years")
        
        return SchoolYearRepository.create(**data)

    @staticmethod
    def update_school_year(request_user, year_id, data):
        if not request_user.is_superuser:
            raise PermissionError("Only admin can create school years")

        year = SchoolYearRepository.get_by_id(year_id)
        return SchoolYearRepository.update(year, **data)

    @staticmethod
    def delete_school_year(request_user, year_id):
        if not request_user.is_superuser:
            raise PermissionError("Only admin can create school years")

        year = SchoolYearRepository.get_by_id(year_id)
        return SchoolYearRepository.delete(year)