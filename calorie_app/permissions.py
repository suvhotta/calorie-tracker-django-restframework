from django.contrib.auth.models import Group, User
from rest_framework import permissions
from calorie_app.models import FoodItem

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
        if isinstance(obj, FoodItem):
            return obj.user == request.user or has_group_permission    
        return obj == request.user or has_group_permission

class IsUserManagerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only a usermanager/admin to modify User accounts.
    """
    required_groups = ['Administrator', 'User_Manager']
    # def has_permission(self, request, view):
    #     has_group_permission = _has_group_permission(request.user, self.required_groups)
    #     return request.user and has_group_permission

    def has_object_permission(self, request, view, obj):
        has_group_permission = _has_group_permission(request.user, self.required_groups)
        if isinstance(obj, FoodItem):
            return obj.user == request.user or has_group_permission    
        return obj == request.user or has_group_permission