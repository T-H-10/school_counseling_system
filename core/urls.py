from rest_framework.routers import DefaultRouter

from django.conf import settings

from .views import (
    AdminArchiveViewSet,
    BackupViewSet,
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

# Backup/restore is a desktop/hybrid concept — cloud relies on the managed
# provider's own backups (see docs/completion-plan.md Step C2) and always has
# the backup_data/restore_data management commands regardless of this route.
if settings.IS_LOCAL_MODE:
    router.register(r"backup", BackupViewSet, basename="backup")

urlpatterns = router.urls
