from rest_framework.routers import DefaultRouter

from .views import (
    AdminArchiveViewSet,
    ClassLevelViewSet,
    CounselorViewSet,
    DocumentViewSet,
    LessonClassAssignmentViewSet,
    LessonPlanViewSet,
    SchoolViewSet,
    SchoolYearViewSet,
    StudentEnrollmentViewSet,
    StudentEventViewSet,
    StudentViewSet,
    SupportRequestViewSet,
)

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")
router.register(r"enrollments", StudentEnrollmentViewSet, basename="enrollments")
router.register(r"studentEvents", StudentEventViewSet, basename="studentEvent")
router.register(r"lessons", LessonPlanViewSet, basename="lesson")
router.register(r"lessonAssignments", LessonClassAssignmentViewSet, basename="lessonAssignment")
router.register(r"schools", SchoolViewSet, basename="school")
router.register(r"classLevels", ClassLevelViewSet, basename="classLevel")
router.register(r"schoolYears", SchoolYearViewSet, basename="schoolYear")
router.register(r"counselors", CounselorViewSet, basename="counselor")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"support", SupportRequestViewSet, basename="support")
router.register(r"archive", AdminArchiveViewSet, basename="archive")

urlpatterns = router.urls
