from rest_framework import permissions
from django.contrib.auth.models import Group


def _is_in_group(user, group_name):
    """
    Checks if user is in a certain group or not.
    """
    try:
        return user.groups.filter(name=group_name).exists()
    except Group.DoesNotExist:
        return None


def _has_group_permission(user, required_groups):
    return any([_is_in_group(user, group_name)for group_name in required_groups])


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only a user/admin to modify calories.
    """
    required_groups = ['Administrator']

    def has_object_permission(self, request, view, obj):
        has_group_permission = _has_group_permission(request.user, self.required_groups)
        return obj.user == request.user or has_group_permission