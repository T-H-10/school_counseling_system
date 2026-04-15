from core.models import Student
from core.helpers import ensure_same_school

class StudentService:

    @staticmethod
    def create_student(user, data):
        
        school = user.counselor.school
        clean_data = {
            k: v for k, v in data.items()
            if k != "school"
        }
        
        return Student.objects.create(school = school, **clean_data)
    
    
    @staticmethod
    def update_student(user, student, data): 

        ensure_same_school(user, student)

        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school", "id"]
        }

        for attr, value in clean_data.items():
                setattr(student, attr, value)

        student.save()
        return student
    

    @staticmethod
    def delete_student(user, student):

        ensure_same_school(user, student)
        student.delete()

