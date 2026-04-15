# class BaseRepository:

#     model = None

#     @classmethod
#     def get_all(cls):
#         return cls.model.objects.all()

#     @classmethod
#     def get_by_id(cls, obj_id):
#         return cls.model.objects.filter(id=obj_id).first()

#     @classmethod
#     def create(cls, **data):
#         return cls.model.objects.create(**data)

#     @classmethod
#     def update(cls, instance, **data):
#         for attr, value in data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance

#     @classmethod
#     def delete(cls, instance):
#         instance.delete()