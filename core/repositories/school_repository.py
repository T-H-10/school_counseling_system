# from core.models import School


# class SchoolRepository:

#     @staticmethod
#     def create(**data):
#         return School.objects.create(**data)

#     @staticmethod
#     def get_by_id(school_id):
#         return School.objects.filter(id=school_id).first()
    
#     @staticmethod
#     def get_all():
#         return School.objects.all()

#     @staticmethod
#     def update(school, **data):
#         for attr, value in data.items():
#             setattr(school, attr, value)
#         school.save()
#         return school

#     @staticmethod
#     def delete(school):
#         school.delete()