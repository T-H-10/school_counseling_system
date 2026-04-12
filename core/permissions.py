from rest_framework.permissions import BasePermission

class IsCounselor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "counselor")
        )
    

class IsSameSchoolStudent(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.school == request.user.counselor.school