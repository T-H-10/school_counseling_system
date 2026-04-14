from core.repositories.class_level_repository import ClassLevelRepository


class ClassLevelService:

    @staticmethod
    def create_class_level(data):
        return ClassLevelRepository.create(**data)

    @staticmethod
    def update_class_level(level_id, data):
        level = ClassLevelRepository.get_by_id(level_id)
        return ClassLevelRepository.update(level, data)

    @staticmethod
    def delete_class_level(level_id):
        level = ClassLevelRepository.get_by_id(level_id)
        return ClassLevelRepository.delete(level)