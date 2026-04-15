from core.repositories.school_repository import SchoolRepository


class SchoolService:

    @staticmethod
    def create_school(data):

        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin allowed")
        
        return SchoolRepository.create(**data)

    @staticmethod
    def update_school(school, data):

        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin allowed")
        
        return SchoolRepository.update(school, **data)

    @staticmethod
    def delete_school(school):
        
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin allowed")
        
        return SchoolRepository.delete(school)