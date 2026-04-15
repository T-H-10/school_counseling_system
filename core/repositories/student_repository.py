from ..models import Student


class StudentRepository:

    @staticmethod
    def get_all():
        return Student.objects.all()
    
    @staticmethod
    def get_by_id(student_id):
        return Student.objects.filter(id = student_id).first()
    
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
