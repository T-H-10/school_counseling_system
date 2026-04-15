from core.repositories.school_year_repository import SchoolYearRepository


class SchoolYearService:

    @staticmethod
    def create_school_year(data):
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin can create school years")
        
        return SchoolYearRepository.create(**data)

    @staticmethod
    def update_school_year(year, data):
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin can create school years")

        return SchoolYearRepository.update(year, **data)

    @staticmethod
    def delete_school_year(year):
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin can create school years")

        return SchoolYearRepository.delete(year)