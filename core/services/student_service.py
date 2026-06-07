from django.db import IntegrityError, transaction
from core.models import Student, StudentEnrollment
from core.helpers import ensure_same_school
from rest_framework.exceptions import ValidationError

class StudentService:

    @staticmethod
    def create_student(user, data):
        school = user.counselor.school

        school_year = data.get('school_year')
        class_level = data.get('class_level')
        class_number = data.get('class_number')

        allowed_fields = {
            "full_name", "id_number", "address",
            "mother_name", "mother_phone", "father_name", "father_phone",
        }
        clean_data = {k: v for k, v in data.items() if k in allowed_fields}

        try:
            with transaction.atomic():
                student = Student.objects.create(school=school, **clean_data)
                StudentEnrollment.objects.create(
                    student=student,
                    school_year=school_year,
                    class_level=class_level,
                    class_number=class_number,
                    school=school,
                )
                return student
        except IntegrityError:
            raise ValidationError({
                "id_number": ["תלמיד עם תעודת זהות זו כבר קיים בבית הספר"]
            })
            
    
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

