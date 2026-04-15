from core.models import Student
from core.repositories.student_repository import StudentRepository


class StudentService:

    @staticmethod
    def create_student(user, data):
        
        school = user.counselor.school
        return StudentRepository.create(school = school, **data)
    
    
    @staticmethod
    def update_student(user, student, data): 

        if student.school != user.counselor.school:
            raise PermissionError("No access to this student")
        
        return StudentRepository.update(student, **data)
    

    @staticmethod
    def delete_student(user, student):

        if student.school != user.counselor.school:
            raise PermissionError("No access to this student")

        StudentRepository.delete(student)

