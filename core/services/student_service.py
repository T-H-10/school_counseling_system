from core.models import Student
from core.repositories.student_repository import StudentRepository


class StudentService:

    @staticmethod
    def create_student(user, data):
        
        school = user.counselor.school
        return StudentRepository.create(school = school, **data)
    
    
    @staticmethod
    def update_student(user, student_id, data): 

        student = StudentRepository.get_by_id(user, student_id)
        
        if student.school != user.counselor.school:
            raise PermissionError("No access to this student")
        
        return StudentRepository.update(student, **data)
    

    @staticmethod
    def delete_student(user, student_id):
        student = StudentRepository.get_by_id(student_id)

        if student.school != user.counselor.school:
            raise PermissionError("No access to this student")

        StudentRepository.delete(student)

