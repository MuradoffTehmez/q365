import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    """Notification consumer for real-time notifications"""
    
    async def connect(self):
        """Connect to WebSocket"""
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.user_group_name = f'user_{self.scope["user"].id}'
            
            # Join user group
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            
            await self.accept()
    
    async def disconnect(self, close_code):
        """Disconnect from WebSocket"""
        if hasattr(self, 'user_group_name'):
            # Leave user group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'mark_as_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_as_read(notification_id)
        elif message_type == 'mark_all_as_read':
            await self.mark_all_notifications_as_read()
    
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        notification = event['notification']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification
        }))
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.scope["user"]
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_notifications_as_read(self):
        """Mark all notifications as read"""
        notifications = Notification.objects.filter(
            recipient=self.scope["user"],
            is_read=False
        )
        notifications.update(is_read=True, read_at=timezone.now())
        return True