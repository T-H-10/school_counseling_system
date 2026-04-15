from core.repositories.class_level_repository import ClassLevelRepository


class ClassLevelService:

    @staticmethod
    def create_class_level(data):
        return ClassLevelRepository.create(**data)

    @staticmethod
    def update_class_level(level, data):
        return ClassLevelRepository.update(level, **data)

    @staticmethod
    def delete_class_level(level):
        return ClassLevelRepository.delete(level)