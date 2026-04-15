from core.models import ClassLevel


class ClassLevelRepository:

    @staticmethod
    def create(**data):
        return ClassLevel.objects.create(**data)

    @staticmethod
    def get_by_id(level_id):
        return ClassLevel.objects.filter(id=level_id).first()
    
    @staticmethod
    def get_all():
        return ClassLevel.objects.all()

    @staticmethod
    def update(level, **data):
        for attr, value in data.items():
            setattr(level, attr, value)
        level.save()
        return level

    @staticmethod
    def delete(level):
        level.delete()