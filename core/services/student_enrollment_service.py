from core.repositories.student_enrollment_repository import StudentEnrollmentRepository
from core.helpers import ensure_same_school

class StudentEnrollmentService:

    @staticmethod
    def create_enrollment(user, data):
                
        school = user.counselor.school        
        student = data["student"]
        ensure_same_school(user, student)

        data.pop("school", None)


        return StudentEnrollmentRepository.create(
            student=student,
            school_year=data["school_year"],
            class_level=data.get("class_level"),
            class_number=data["class_number"],
            school=school 
        )

    @staticmethod
    def update_enrollment(user, enrollment, data):
        
        ensure_same_school(user, enrollment)
        
        data.pop("school", None)
        data.pop("student", None)
        data.pop("school_year", None)

        return StudentEnrollmentRepository.update(enrollment, **data)

    @staticmethod
    def delete_enrollment(user, enrollment):

        ensure_same_school(user, enrollment)
        return StudentEnrollmentRepository.delete(enrollment)