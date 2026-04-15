from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .services.student_service import StudentService
from .services.student_enrollment_service import StudentEnrollmentService
from .services.student_event_service import StudentEventService
from .services.class_session_service import ClassSessionService
from .services.school_service import SchoolService
from .services.class_level_service import ClassLevelService
from .services.school_year_service import SchoolYearService
from .services.counselor_service import CounselorService

from .models import Student, StudentEnrollment, StudentEvent, ClassSession, School, ClassLevel, SchoolYear, Counselor
from .serializers import StudentSerializer, StudentEnrollmentSerializer, StudentEventSerializer, ClassSessionSerializer, SchoolSerializer, ClassLevelSerializer, SchoolYearSerializer, CounselorSerializer
from .permissions import IsCounselor, IsOwnerSchool

class StudentViewSet(ModelViewSet):
    permission_classes = [IsCounselor, IsOwnerSchool]
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        student = StudentService.create_student(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = student

    def perform_update(self, serializer):
        student = StudentService.update_student(
            self.request.user,
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = student

    def perform_destroy(self, instance):
        StudentService.delete_student(
            self.request.user,
            instance.id
        )


class StudentEnrollmentViewSet(ModelViewSet):
    permission_classes = [IsCounselor, IsOwnerSchool]
    serializer_class = StudentEnrollmentSerializer

    def get_queryset(self):
        return StudentEnrollment.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        enrollment = StudentEnrollmentService.create_enrollment(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = enrollment

    def perform_update(self, serializer):
        enrollment = StudentEnrollmentService.update_enrollment(
            self.request.user,
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = enrollment

    def perform_destroy(self, instance):
        StudentEnrollmentService.delete_enrollment(
            self.request.user,
            instance.id
        ) 


class StudentEventViewSet(ModelViewSet):
    permission_classes = [IsCounselor, IsOwnerSchool]
    serializer_class = StudentEventSerializer

    def get_queryset(self):
        return StudentEvent.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        event = StudentEventService.create_event(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = event

    def perform_update(self, serializer):
        event = StudentEventService.update_event(
            self.request.user,
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = event

    def perform_destroy(self, instance):
        StudentEventService.delete_event(
            self.request.user,
            instance.id
        )        


class ClassSessionViewSet(ModelViewSet):
    permission_classes = [IsCounselor, IsOwnerSchool]
    serializer_class = ClassSessionSerializer

    def get_queryset(self):
        return ClassSession.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        session = ClassSessionService.create_session(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = session

    def perform_update(self, serializer):
        session = ClassSessionService.update_session(
            self.request.user,
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = session

    def perform_destroy(self, instance):
        ClassSessionService.delete_session(
            self.request.user,
            instance.id
        )


class SchoolViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def perform_create(self, serializer):
        school = SchoolService.create_school(serializer.validated_data)
        serializer.instance = school

    def perform_update(self, serializer):
        school = SchoolService.update_school(
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = school

    def perform_destroy(self, instance):
        SchoolService.delete_school(instance.id)        


class ClassLevelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ClassLevel.objects.all()
    serializer_class = ClassLevelSerializer

    def perform_create(self, serializer):
        level = ClassLevelService.create_class_level(serializer.validated_data)
        serializer.instance = level

    def perform_update(self, serializer):
        level = ClassLevelService.update_class_level(
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = level

    def perform_destroy(self, instance):
        ClassLevelService.delete_class_level(instance.id)


class SchoolYearViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer

    def perform_create(self, serializer):
        year = SchoolYearService.create_school_year(serializer.validated_data)
        serializer.instance = year

    def perform_update(self, serializer):
        year = SchoolYearService.update_school_year(
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = year

    def perform_destroy(self, instance):
        SchoolYearService.delete_school_year(instance.id)


class CounselorViewSet(ModelViewSet):
    permission_classes = [IsCounselor]
    queryset = Counselor.objects.all()
    serializer_class = CounselorSerializer

    def perform_create(self, serializer):
        counselor = CounselorService.create_counselor(serializer.validated_data)
        serializer.instance = counselor

    def perform_update(self, serializer):
        counselor = CounselorService.update_counselor(
            self.get_object().id,
            serializer.validated_data
        )
        serializer.instance = counselor

    def perform_destroy(self, instance):
        CounselorService.delete_counselor(instance.id)