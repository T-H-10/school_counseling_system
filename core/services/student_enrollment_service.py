from core.repositories.student_enrollment_repository import StudentEnrollmentRepository
from core.models import ClassLevel, SchoolYear, Student


class StudentEnrollmentService:

    @staticmethod
    def create_enrollment(user, data):
                
        school = user.counselor.school        
        student = Student.objects.for_user(user).get(id=data["student"])
        school_year = SchoolYear.objects.get(id=data["school_year"])
        
        class_level = None
        if data.get("class_level"):
            class_level = ClassLevel.objects.get(id=data["class_level"])

        return StudentEnrollmentRepository.create(
            student=student,
            school_year=school_year,
            class_level=class_level,
            class_number=data["class_number"],
            school=school 
        )

    @staticmethod
    def update_enrollment(user, enrollment_id, data):
        
        enrollment = StudentEnrollmentRepository.get_by_id(user, enrollment_id)
        return StudentEnrollmentRepository.update(enrollment, data)

    @staticmethod
    def delete_enrollment(user, enrollment_id):

        enrollment = StudentEnrollmentRepository.get_by_id(user, enrollment_id)
        StudentEnrollmentRepository.delete(enrollment)