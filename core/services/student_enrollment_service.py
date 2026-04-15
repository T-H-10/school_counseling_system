from core.models import StudentEnrollment
from core.helpers import ensure_same_school

class StudentEnrollmentService:

    @staticmethod
    def create_enrollment(user, data):
                
        school = user.counselor.school        
        student = data["student"]

        ensure_same_school(user, student)

        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school"]
        }

        return StudentEnrollment.objects.create(
            student=student,
            school_year=clean_data["school_year"],
            class_level=clean_data.get("class_level"),
            class_number=clean_data["class_number"],
            school=school 
        )

    @staticmethod
    def update_enrollment(user, enrollment, data):
        
        ensure_same_school(user, enrollment)
        
        clean_data = {
            k: v for k, v in data.items()
            if k not in ["school", "student", "school_year", "id"]
        }
            
        for attr, value in clean_data.items():
            setattr(enrollment, attr, value)

        enrollment.save()
        return enrollment
    
    @staticmethod
    def delete_enrollment(user, enrollment):

        ensure_same_school(user, enrollment)
        enrollment.delete()