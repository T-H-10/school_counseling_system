from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

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
from .permissions import IsCounselor

class StudentViewSet(ModelViewSet):
    permission_classes = [IsCounselor]
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.filter(
            school = self.request.user.counselor.school
        )

    def perform_create(self, serializer):
        student = StudentService.create_student(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = student

    def perform_update(self, serializer):
        student = StudentService.update_student(
            self.request.user,
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = student

    def perform_destroy(self, instance):
        StudentService.delete_student(
            self.request.user,
            instance
        )


class StudentEnrollmentViewSet(ModelViewSet):
    permission_classes = [IsCounselor]
    serializer_class = StudentEnrollmentSerializer

    def get_queryset(self):
        return StudentEnrollment.objects.filter(
            school = self.request.user.counselor.school
        )

    def perform_create(self, serializer):
        enrollment = StudentEnrollmentService.create_enrollment(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = enrollment

    def perform_update(self, serializer):
        enrollment = StudentEnrollmentService.update_enrollment(
            self.request.user,
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = enrollment

    def perform_destroy(self, instance):
        StudentEnrollmentService.delete_enrollment(
            self.request.user,
            instance
        ) 


class StudentEventViewSet(ModelViewSet):
    permission_classes = [IsCounselor]
    serializer_class = StudentEventSerializer

    def get_queryset(self):
        return StudentEvent.objects.filter(
            school = self.request.user.counselor.school
        )

    def perform_create(self, serializer):
        event = StudentEventService.create_event(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = event

    def perform_update(self, serializer):
        event = StudentEventService.update_event(
            self.request.user,
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = event

    def perform_destroy(self, instance):
        StudentEventService.delete_event(
            self.request.user,
            instance
        )        


class ClassSessionViewSet(ModelViewSet):
    permission_classes = [IsCounselor]
    serializer_class = ClassSessionSerializer

    def get_queryset(self):
        return ClassSession.objects.filter(
            school = self.request.user.counselor.school
        )

    def perform_create(self, serializer):
        session = ClassSessionService.create_session(
            self.request.user,
            serializer.validated_data
        )
        serializer.instance = session

    def perform_update(self, serializer):
        session = ClassSessionService.update_session(
            self.request.user,
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = session

    def perform_destroy(self, instance):
        ClassSessionService.delete_session(
            self.request.user,
            instance
        )


class SchoolViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def perform_create(self, serializer):
        school = SchoolService.create_school(serializer.validated_data)
        serializer.instance = school

    def perform_update(self, serializer):
        school = SchoolService.update_school(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = school

    def perform_destroy(self, instance):
        SchoolService.delete_school(instance)        


class ClassLevelViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ClassLevel.objects.all()
    serializer_class = ClassLevelSerializer

    def perform_create(self, serializer):
        level = ClassLevelService.create_class_level(serializer.validated_data)
        serializer.instance = level

    def perform_update(self, serializer):
        level = ClassLevelService.update_class_level(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = level

    def perform_destroy(self, instance):
        ClassLevelService.delete_class_level(instance)


class SchoolYearViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer

    def perform_create(self, serializer):
        year = SchoolYearService.create_school_year(serializer.validated_data)
        serializer.instance = year

    def perform_update(self, serializer):
        year = SchoolYearService.update_school_year(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = year

    def perform_destroy(self, instance):
        SchoolYearService.delete_school_year(
            instance
            )


class CounselorViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Counselor.objects.all()
    serializer_class = CounselorSerializer

    def perform_create(self, serializer):
        counselor = CounselorService.create_counselor(
            serializer.validated_data
            )
        serializer.instance = counselor

    def perform_update(self, serializer):
        counselor = CounselorService.update_counselor(
            self.get_object(),
            serializer.validated_data
        )
        serializer.instance = counselor

    def perform_destroy(self, instance):
        CounselorService.delete_counselor(
            instance
        )
    
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reset_password(self, request, pk = None):
        counselor = self.get_object()

        CounselorService.reset_password(
            counselor,
            request.data["new_password"]
        )

        return Response({"status": "password updated"})