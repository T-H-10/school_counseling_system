from rest_framework.permissions import BasePermission


class IsCounselor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "counselor")


class DocumentAccessPolicy(IsCounselor):
    """Permission for document endpoints. Delegates to IsCounselor today.

    Extend here when future roles (principal, VP) need different access rules
    without touching any other viewset.
    """

    pass
