from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object or admin.
        return obj == request.user or request.user.is_staff


class HasRolePermission(permissions.BasePermission):
    """
    Custom permission to check if user has a specific permission through roles.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Get required permission from view
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True
        
        # Check if user has the required permission through roles
        user_roles = request.user.user_roles.all()
        for user_role in user_roles:
            if user_role.role.permissions.filter(codename=required_permission).exists():
                return True
        
        return False