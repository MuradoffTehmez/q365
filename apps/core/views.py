from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import (
    Role, Permission, UserRole, Organization, 
    Department, Sector, Team, Notification, Reminder
)
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PermissionSerializer, RoleSerializer, UserRoleSerializer,
    OrganizationSerializer, DepartmentSerializer, SectorSerializer, TeamSerializer,
    NotificationSerializer, ReminderSerializer
)
from .permissions import IsOwnerOrAdmin, HasRolePermission

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User viewset"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerOrAdmin]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        if not (request.user.is_staff or request.user == user):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {"detail": "Both old_password and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({"detail": "Password updated successfully."})


class RoleViewSet(viewsets.ModelViewSet):
    """Role viewset"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_roles'


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Permission viewset (read-only)"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRoleViewSet(viewsets.ModelViewSet):
    """User role viewset"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_roles'
    
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class OrganizationViewSet(viewsets.ModelViewSet):
    """Organization viewset"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_organizations'


class DepartmentViewSet(viewsets.ModelViewSet):
    """Department viewset"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_departments'


class SectorViewSet(viewsets.ModelViewSet):
    """Sector viewset"""
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_sectors'


class TeamViewSet(viewsets.ModelViewSet):
    """Team viewset"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    required_permission = 'manage_teams'


class NotificationViewSet(viewsets.ModelViewSet):
    """Notification viewset"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({"detail": "Notification marked as read."})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True, read_at=timezone.now())
        return Response({"detail": "All notifications marked as read."})


class ReminderViewSet(viewsets.ModelViewSet):
    """Reminder viewset"""
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_completed(self, request, pk=None):
        """Mark reminder as completed"""
        reminder = self.get_object()
        reminder.is_completed = True
        reminder.completed_at = timezone.now()
        reminder.save()
        return Response({"detail": "Reminder marked as completed."})