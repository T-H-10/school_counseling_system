from core.models import Student
from core.repositories.student_repository import StudentRepository


class StudentService:

    @staticmethod
    def create_student(user, data):
        
        if not hasattr(user, "counselor"):
            raise ValueError("Not a counselor")
            
        school = user.counselor.school
        return StudentRepository.create(school = school, **data)
    
    
    @staticmethod
    def update_student(user, student_id, data): 

        if not hasattr(user, "counselor"):
            raise ValueError("User is not a counselor")
        
        student = StudentRepository.get_by_id(user, student_id)
        return StudentRepository.update(student, **data)
    

    @staticmethod
    def delete_student(user, student_id):
        student = StudentRepository.get_by_id(user, student_id)
        StudentRepository.delete(student)

