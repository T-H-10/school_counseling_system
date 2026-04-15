from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentEnrollmentViewSet, StudentEventViewSet, ClassSessionViewSet, SchoolViewSet, ClassLevelViewSet, SchoolYearViewSet, CounselorViewSet

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")
router.register(r"enrollments", StudentEnrollmentViewSet, basename="enrollments")
router.register(r"studentEvent", StudentEventViewSet, basename="studentEvent")
router.register(r"classSession", ClassSessionViewSet, basename="classSession")
router.register(r"school", SchoolViewSet, basename="school")
router.register(r"classLevel", ClassLevelViewSet, basename="classLevel")
router.register(r"schoolYear", SchoolYearViewSet, basename="schoolYear")
router.register(r"counselor", CounselorViewSet, basename="counselor")
                
urlpatterns = router.urls
