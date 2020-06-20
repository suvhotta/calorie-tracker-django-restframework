from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permission to allow only a user to modify it's calories.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user