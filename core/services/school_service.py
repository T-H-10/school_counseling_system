from core.repositories.school_repository import SchoolRepository


class SchoolService:

    @staticmethod
    def create_school(data):
        return SchoolRepository.create(**data)

    @staticmethod
    def update_school(school_id, data):
        school = SchoolRepository.get_by_id(school_id)
        return SchoolRepository.update(school, data)

    @staticmethod
    def delete_school(school_id):
        school = SchoolRepository.get_by_id(school_id)
        return SchoolRepository.delete(school)