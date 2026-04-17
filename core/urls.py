from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentEnrollmentViewSet, StudentEventViewSet, ClassSessionViewSet, SchoolViewSet, ClassLevelViewSet, SchoolYearViewSet, CounselorViewSet

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="students")
router.register(r"enrollments", StudentEnrollmentViewSet, basename="enrollments")
router.register(r"studentEvents", StudentEventViewSet, basename="studentEvent")
router.register(r"classSessions", ClassSessionViewSet, basename="classSession")
router.register(r"schools", SchoolViewSet, basename="school")
router.register(r"classLevels", ClassLevelViewSet, basename="classLevel")
router.register(r"schoolYears", SchoolYearViewSet, basename="schoolYear")
router.register(r"counselors", CounselorViewSet, basename="counselor")
                
urlpatterns = router.urls
