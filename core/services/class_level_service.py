from core.repositories.class_level_repository import ClassLevelRepository


class ClassLevelService:

    @staticmethod
    def create_class_level(request_user, data):
        if not request_user.is_superuser:
            raise PermissionError("Only admin")
        return ClassLevelRepository.create(**data)

    @staticmethod
    def update_class_level(request_user, level_id, data):
        if not request_user.is_superuser:
            raise PermissionError("Only admin")

        level = ClassLevelRepository.get_by_id(level_id)
        return ClassLevelRepository.update(level, **data)

    @staticmethod
    def delete_class_level(request_user, level_id):
        if not request_user.is_superuser:
            raise PermissionError("Only admin")

        level = ClassLevelRepository.get_by_id(level_id)
        return ClassLevelRepository.delete(level)