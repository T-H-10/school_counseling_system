from core.repositories.school_repository import SchoolRepository


class SchoolService:

    @staticmethod
    def create_school(request_user, data):

        if not request_user.is_superuser:
            raise PermissionError("Only admin allowed")
        
        return SchoolRepository.create(**data)

    @staticmethod
    def update_school(request_user, school_id, data):

        if not request_user.is_superuser:
            raise PermissionError("Only admin allowed")
        
        school = SchoolRepository.get_by_id(school_id)
        return SchoolRepository.update(school, **data)

    @staticmethod
    def delete_school(request_user, school_id):
        
        if not request_user.is_superuser:
            raise PermissionError("Only admin allowed")
        
        school = SchoolRepository.get_by_id(school_id)
        return SchoolRepository.delete(school)