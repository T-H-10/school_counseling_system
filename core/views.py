from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .services.student_service import StudentService
from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        student = StudentService.create_student(
            self.request.user,
            serializer.validate_data
        )
        serializer.instance = student

    def perform_update(self, serializer):
        student = StudentService.update_student(
            self.request.user,
            self.get_object().id,
            serializer.validate_data
        )
        serializer.instance = student

    def perform_destroy(self, instance):
        StudentService.delete_student(
            self.request.user,
            instance.id
        )