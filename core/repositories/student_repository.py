from ..models import Student


class StudentRepository:

    @staticmethod
    def get_for_user(user):
        return Student.objects.filter(user)
    
    @staticmethod
    def get_by_id(user, student_id):
        return Student.objects.get(student_id, user)
    
    @staticmethod
    def create(**data):
        return Student.objects.create(**data)
    
    @staticmethod
    def update(student, **data):
        for attr, value in data.items():
            setattr(student, attr, value)

        student.save()
        return student
    
    @staticmethod
    def delete(student):
        student.delete()
