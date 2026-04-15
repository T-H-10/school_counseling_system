from core.models import StudentEnrollment
from core.helpers import ensure_same_school

class StudentEnrollmentService:

    @staticmethod
    def create_enrollment(user, data):
                
        school = user.counselor.school        
        student = data["student"]

        ensure_same_school(user, student)

        data.pop("school", None)


        return StudentEnrollment.objects.create(
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
        data.pop("id", None)

        for attr, value in data.items():
            setattr(enrollment, attr, value)

        enrollment.save()
        return enrollment
    
    @staticmethod
    def delete_enrollment(user, enrollment):

        ensure_same_school(user, enrollment)
        enrollment.delete()