from core.models import Student


class StudentService:

    @staticmethod
    def create_student(user, validated_data):
        school = user.counselor.school

        student = Student.objects.create(
            school = school,
            **validated_data
        )

        return student
    
    @staticmethod
    def get_students(user):
        return Student.objects.for_user(user)