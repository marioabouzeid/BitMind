from rest_framework import permissions


class ReadOnlyOrAdminOnly(permissions.BasePermission):
    """
    Custom permission to allow superusers to perform any action and
    grant read-only access to regular users.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True  # Superusers can perform any action
        elif request.method in permissions.SAFE_METHODS:
            return True  # Regular users can perform safe methods (GET, HEAD, OPTIONS)
        else:
            return (
                False  # Regular users can't perform other actions (POST, PUT, DELETE)
            )
