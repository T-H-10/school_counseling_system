from core.models import ClassLevel


class ClassLevelService:

    @staticmethod
    def create_class_level(data):
        clean_data = {
            k: v for k, v in data.items()
            if k != "id"
        }

        return ClassLevel.objects.create(**clean_data)

    @staticmethod
    def update_class_level(level, data):
        
        clean_data = {
            k: v for k, v in data.items()
            if k != "id"
        }

        for attr, value in clean_data.items():
            setattr(level, attr, value)
        level.save()
        return level
    
    @staticmethod
    def delete_class_level(level):
        level.delete()