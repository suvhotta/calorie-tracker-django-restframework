from django.contrib.auth.models import Group
from rest_framework import permissions

# def _is_in_group(user, group_name):
#     """
#     Checks if user is in a certain group or not.
#     """
#     try:
#         return user.groups.filter(name=group_name).exists()
#     except Group.DoesNotExist:
#         return None


def _has_group_permission(user, required_groups):
    try:
        return any([user.groups.filter(name=group_name).exists() for group_name in required_groups])
    except Group.DoesNotExist:
        return None

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only a user/admin to modify calories.
    """
    required_groups = ['Administrator']

    def has_object_permission(self, request, view, obj):
        has_group_permission = _has_group_permission(request.user, self.required_groups)
        return obj == request.user or has_group_permission


class IsUserManagerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only a usermanager/admin to modify User accounts.
    """
    required_groups = ['Administrator', 'User_Manager']
    def has_object_permission(self, request, view, obj):
        has_group_permission = _has_group_permission(request.user, self.required_groups)
        return obj == request.user or has_group_permission
