from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .services.student_service import StudentService
from .models import Student
from .serializers import StudentSerializer
from .permissions import IsCounselor, IsSameSchoolStudent

class StudentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsCounselor, IsSameSchoolStudent]
    serializer_class = StudentSerializer

    def get_queryset(self):
        user = self.request.user
        return Student.objects.for_user(user)

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
            instance.id
        )