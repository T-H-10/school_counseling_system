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
    

    @staticmethod
    def get_student(user, student_id):
        return Student.objects.for_user(user).filter(id=student_id).first()
    
    @staticmethod
    def update_student(user, student_id, validated_data):
        student = StudentService.get_student(user,student_id)

        if not student:
            return None
        
        for attr, value in validated_data.items():
            setattr(student, attr, value)

        student.save()
        return student
    

    @staticmethod
    def delete_student(user, student_id):
        student = StudentService.get_student(user, student_id)

        if not student:
            return False
        
        student.delete()
        return True

