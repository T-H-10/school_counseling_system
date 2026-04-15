from core.repositories.student_enrollment_repository import StudentEnrollmentRepository


class StudentEnrollmentService:

    @staticmethod
    def create_enrollment(user, data):
                
        school = user.counselor.school        
        student = data["student"]

        if student.school != school:
            raise PermissionError("Student does not belong to your school")

        return StudentEnrollmentRepository.create(
            student=student,
            school_year=data["school_year"],
            class_level=data.get("class_level"),
            class_number=data["class_number"],
            school=school 
        )

    @staticmethod
    def update_enrollment(user, enrollment, data):
        
        if enrollment.school != user.counselor.school:
            raise PermissionError("Not allowed")
        
        data.pop("school", None)
        data.pop("student", None)
        data.pop("school_year", None)

        return StudentEnrollmentRepository.update(enrollment, **data)

    @staticmethod
    def delete_enrollment(user, enrollment):

        if enrollment.school != user.counselor.school:
            raise PermissionError("Not allowed")
        
        StudentEnrollmentRepository.delete(enrollment)