from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    StudentEnrollmentViewSet,
    StudentEventViewSet,
    LessonPlanViewSet,
    LessonClassAssignmentViewSet,
    SchoolViewSet,
    ClassLevelViewSet,
    SchoolYearViewSet,
    CounselorViewSet,
    DocumentViewSet,
)

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")
router.register(r"enrollments", StudentEnrollmentViewSet, basename="enrollments")
router.register(r"studentEvents", StudentEventViewSet, basename="studentEvent")
router.register(r"lessons", LessonPlanViewSet, basename="lesson")
router.register(
    r"lessonAssignments", LessonClassAssignmentViewSet, basename="lessonAssignment"
)
router.register(r"schools", SchoolViewSet, basename="school")
router.register(r"classLevels", ClassLevelViewSet, basename="classLevel")
router.register(r"schoolYears", SchoolYearViewSet, basename="schoolYear")
router.register(r"counselors", CounselorViewSet, basename="counselor")
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = router.urls
