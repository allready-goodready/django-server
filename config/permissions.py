from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    SAFE_METHODS(GET, HEAD, OPTIONS)은 모두 허용.
    그 외(POST, PUT, PATCH, DELETE)는 obj.user == request.user인 경우에만 허용.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user", None) == request.user
