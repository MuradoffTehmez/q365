from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Reminder, Notification

User = get_user_model()

class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def create_notification(recipient, title, message, level='info', icon=None, link=None, data=None):
        """Create a new notification"""
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            level=level,
            icon=icon,
            link=link,
            data=data or {}
        )
    
    @staticmethod
    def send_bulk_notifications(recipients, title, message, level='info', icon=None, link=None, data=None):
        """Send notifications to multiple recipients"""
        notifications = []
        for recipient in recipients:
            notifications.append(
                Notification(
                    recipient=recipient,
                    title=title,
                    message=message,
                    level=level,
                    icon=icon,
                    link=link,
                    data=data or {}
                )
            )
        return Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        notifications = Notification.objects.filter(recipient=user, is_read=False)
        notifications.update(is_read=True, read_at=timezone.now())
        return notifications.count()

class ReminderService:
    """Service for managing reminders"""
    
    @staticmethod
    def create_reminder(user, title, remind_at, description=None, link=None, data=None):
        """Create a new reminder"""
        return Reminder.objects.create(
            user=user,
            title=title,
            description=description or '',
            remind_at=remind_at,
            link=link,
            data=data or {}
        )
    
    @staticmethod
    def get_due_reminders():
        """Get all due reminders"""
        return Reminder.objects.filter(
            remind_at__lte=timezone.now(),
            is_completed=False
        )
    
    @staticmethod
    def complete_reminder(reminder_id, user):
        """Mark a reminder as completed"""
        try:
            reminder = Reminder.objects.get(id=reminder_id, user=user)
            reminder.is_completed = True
            reminder.completed_at = timezone.now()
            reminder.save()
            return True
        except Reminder.DoesNotExist:
            return False

class PermissionService:
    """Service for checking user permissions"""
    
    @staticmethod
    def user_has_permission(user, permission_codename):
        """Check if user has a specific permission"""
        if user.is_superuser:
            return True
        
        # Check user roles
        user_roles = user.user_roles.filter(
            is_active=True
        ).select_related('role')
        
        for user_role in user_roles:
            # Check if role is expired
            if user_role.is_expired:
                continue
            
            # Check if role has the permission
            if user_role.role.permissions.filter(
                codename=permission_codename,
                is_active=True
            ).exists():
                return True
        
        return False
    
    @staticmethod
    def user_has_any_permission(user, permission_codenames):
        """Check if user has any of the specified permissions"""
        return any(
            PermissionService.user_has_permission(user, codename)
            for codename in permission_codenames
        )
    
    @staticmethod
    def user_has_all_permissions(user, permission_codenames):
        """Check if user has all of the specified permissions"""
        return all(
            PermissionService.user_has_permission(user, codename)
            for codename in permission_codenames
        )
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user"""
        if user.is_superuser:
            from .models import Permission
            return Permission.objects.filter(is_active=True)
        
        permissions = set()
        user_roles = user.user_roles.filter(
            is_active=True
        ).select_related('role')
        
        for user_role in user_roles:
            if user_role.is_expired:
                continue
            
            role_permissions = user_role.role.permissions.filter(
                is_active=True
            ).values_list('codename', flat=True)
            permissions.update(role_permissions)
        
        return list(permissions)