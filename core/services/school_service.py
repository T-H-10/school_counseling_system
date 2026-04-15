from core.repositories.school_repository import SchoolRepository


class SchoolService:

    @staticmethod
    def create_school(data):

        return SchoolRepository.create(**data)

    @staticmethod
    def update_school(school, data):

        return SchoolRepository.update(school, **data)

    @staticmethod
    def delete_school(school):
        
        return SchoolRepository.delete(school)