from django.db.models import Q

from core.models import Document, LessonPlan, Student
from core.services.student_enrollment_service import StudentEnrollmentService

RESULT_LIMIT = 5
MIN_QUERY_LENGTH = 1  # class levels/numbers are single characters — don't require 2+


class GlobalSearchService:
    @staticmethod
    def search(user, query):
        query = (query or "").strip()
        if len(query) < MIN_QUERY_LENGTH:
            return {"students": [], "classes": [], "documents": [], "lessons": []}

        school = user.counselor.school

        students = Student.objects.filter(school=school).filter(
            Q(full_name__icontains=query) | Q(id_number__icontains=query)
        )[:RESULT_LIMIT]

        classes = [
            group
            for group in StudentEnrollmentService.get_classes(user)
            if query in (group["class_level__name"] or "") or query in str(group["class_number"])
        ][:RESULT_LIMIT]

        documents = Document.objects.filter(school=school, title__icontains=query)[:RESULT_LIMIT]

        lessons = LessonPlan.objects.filter(school=school, title__icontains=query)[:RESULT_LIMIT]

        return {
            "students": [
                {"id": s.id, "full_name": s.full_name, "id_number": s.id_number} for s in students
            ],
            "classes": [
                {
                    "class_level": g["class_level"],
                    "class_level_name": g["class_level__name"],
                    "class_number": g["class_number"],
                }
                for g in classes
            ],
            "documents": [
                {"id": d.id, "title": d.title, "category": d.category} for d in documents
            ],
            "lessons": [{"id": l.id, "title": l.title} for l in lessons],
        }
