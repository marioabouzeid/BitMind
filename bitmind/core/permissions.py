from rest_framework import permissions


class ReadOnlyOrAdminOnly(permissions.BasePermission):
    """
    Custom permission to allow superusers to perform any action and
    grant read-only access to regular users.
    """

    def has_permission(self, request, view):
        # Superusers can perform any action
        # Regular users can perform safe methods (GET, HEAD, OPTIONS)
        # Regular users can't perform other actions (POST, PUT, DELETE)
        if request.user.is_superuser:
            return True
        else:
            return request.method in permissions.SAFE_METHODS
