from core.repositories.class_level_repository import ClassLevelRepository


class ClassLevelService:

    @staticmethod
    def create_class_level(data):
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin")
        return ClassLevelRepository.create(**data)

    @staticmethod
    def update_class_level(level, data):
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin")

        return ClassLevelRepository.update(level, **data)

    @staticmethod
    def delete_class_level(level):
        # if not request_user.is_superuser:
        #     raise PermissionError("Only admin")

        return ClassLevelRepository.delete(level)