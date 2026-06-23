from core.models import ClassLevel
from core.services.base import apply_fields, create_excluding


class ClassLevelService:
    @staticmethod
    def create_class_level(data):
        return create_excluding(ClassLevel, data)

    @staticmethod
    def update_class_level(level, data):
        return apply_fields(level, data)

    @staticmethod
    def delete_class_level(level):
        level.delete()
