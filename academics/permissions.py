from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Allow read access to any authenticated user.
    Allow write access only to admin users.
    Unauthenticated requests get 403 (Forbidden).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == request.user.Role.ADMIN

class IsAdminOrTeacher(BasePermission):
    """
    Allow read access to any authenticated user.
    Allow write access to admin or teacher users.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in [request.user.Role.ADMIN, request.user.Role.TEACHER]