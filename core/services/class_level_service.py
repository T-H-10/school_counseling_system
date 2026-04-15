from core.models import ClassLevel


class ClassLevelService:

    @staticmethod
    def create_class_level(data):
        return ClassLevel.objects.create(**data)

    @staticmethod
    def update_class_level(level, data):
        for attr, value in data.items():
            setattr(level, attr, value)
        level.save()
        return level
    
    @staticmethod
    def delete_class_level(level):
        level.delete()