from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import User, Role, UserRole, Notification
from .serializers import NotificationSerializer


@receiver(post_save, sender=UserRole)
def user_role_assigned(sender, instance, created, **kwargs):
    """Send notification when a role is assigned to a user"""
    if created:
        notification = Notification.objects.create(
            recipient=instance.user,
            title=_("New Role Assigned"),
            message=_("You have been assigned the role: {role}").format(role=instance.role.name),
            level='info',
            icon='fas fa-user-tag'
        )
        
        # Send real-time notification
        send_real_time_notification(notification)


@receiver(post_delete, sender=UserRole)
def user_role_removed(sender, instance, **kwargs):
    """Send notification when a role is removed from a user"""
    notification = Notification.objects.create(
        recipient=instance.user,
        title=_("Role Removed"),
        message=_("The role {role} has been removed from your account").format(role=instance.role.name),
        level='warning',
        icon='fas fa-user-times'
    )
    
    # Send real-time notification
    send_real_time_notification(notification)


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """Send notification when a new user is created"""
    if created:
        # Notify all admins
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            notification = Notification.objects.create(
                recipient=admin,
                title=_("New User Created"),
                message=_("A new user {user} has been created").format(user=instance.get_full_name() or instance.username),
                level='info',
                icon='fas fa-user-plus'
            )
            
            # Send real-time notification
            send_real_time_notification(notification)


def send_real_time_notification(notification):
    """Send real-time notification via WebSocket"""
    channel_layer = get_channel_layer()
    
    # Serialize notification
    serializer = NotificationSerializer(notification)
    
    # Send to user's group
    async_to_sync(channel_layer.group_send)(
        f'user_{notification.recipient.id}',
        {
            'type': 'notification_message',
            'notification': serializer.data
        }
    )