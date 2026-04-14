from core.models import StudentEnrollment


class StudentEnrollmentRepository:

    @staticmethod
    def create(**data):
        return StudentEnrollment.objects.create(**data)

    @staticmethod
    def get_by_id(user, enrollment_id):
        return StudentEnrollment.objects.for_user(user).get(id=enrollment_id)

    @staticmethod
    def update(enrollment, data):
        for attr, value in data.items():
            setattr(enrollment, attr, value)

        enrollment.save()
        return enrollment

    @staticmethod
    def delete(enrollment):
        enrollment.delete()