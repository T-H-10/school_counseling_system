from core.repositories.student_enrollment_repository import StudentEnrollmentRepository
from core.models import ClassLevel, SchoolYear, Student


class StudentEnrollmentService:

    @staticmethod
    def create_enrollment(user, data):
                
        school = user.counselor.school        

        return StudentEnrollmentRepository.create(
            student=data["student"],
            school_year=data["school_year"],
            class_level=data.get("class_level"),
            class_number=data["class_number"],
            school=school 
        )

    @staticmethod
    def update_enrollment(user, enrollment_id, data):
        
        enrollment = StudentEnrollmentRepository.get_by_id(user, enrollment_id)
        if enrollment.school != user.counselor.school:
            raise PermissionError("Not allowed")
        
        data.pop("school", None)
        data.pop("student", None)
        data.pop("school_year", None)

        return StudentEnrollmentRepository.update(enrollment, data)

    @staticmethod
    def delete_enrollment(user, enrollment_id):

        enrollment = StudentEnrollmentRepository.get_by_id(user, enrollment_id)

        if enrollment.school != user.counselor.school:
            raise PermissionError("Not allowed")
        
        StudentEnrollmentRepository.delete(enrollment)