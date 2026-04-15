from core.models import StudentEnrollment


class StudentEnrollmentRepository:

    @staticmethod
    def create(**data):
        return StudentEnrollment.objects.create(**data)

    @staticmethod
    def get_by_id(enrollment_id):
        return StudentEnrollment.objects.filter(id=enrollment_id).first()
    
    @staticmethod
    def get_all():
        return StudentEnrollment.objects.all()

    @staticmethod
    def update(enrollment, **data):
        for attr, value in data.items():
            setattr(enrollment, attr, value)

        enrollment.save()
        return enrollment

    @staticmethod
    def delete(enrollment):
        enrollment.delete()