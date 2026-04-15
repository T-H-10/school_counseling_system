from core.models import Student
from core.repositories.student_repository import StudentRepository
from core.helpers import ensure_same_school

class StudentService:

    @staticmethod
    def create_student(user, data):
        
        school = user.counselor.school
        data.pop("school", None)

        return Student.objects.create(school = school, **data)
    
    
    @staticmethod
    def update_student(user, student, data): 

        ensure_same_school(user, student)

        data.pop("school", None)
        data.pop("id", None)

        for attr, value in data.items():
                setattr(student, attr, value)

        student.save()
        return student
    

    @staticmethod
    def delete_student(user, student):

        ensure_same_school(user, student)
        student.delete()

