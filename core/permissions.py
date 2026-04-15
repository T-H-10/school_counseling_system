from rest_framework.permissions import BasePermission

class IsCounselor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "counselor")
        )


# class IsOwnerSchool(BasePermission):

#     def has_object_permission(self, request, view, obj):
#         if hasattr(obj, "school"):
#             return obj.school == request.user.counselor.school

#         if hasattr(obj, "student"):
#             return obj.student.school == request.user.counselor.school

#         return False

# class IsAdminUser(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_superuser