from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    """Log model save operations"""
    # Skip audit log model to avoid recursion
    if sender == AuditLog:
        return
    
    # Get current user from thread local
    try:
        from threading import local
        _thread_locals = local()
        user = getattr(_thread_locals, 'user', None)
    except:
        user = None
    
    if user:
        action = 'create' if created else 'update'
        content_type = ContentType.objects.get_for_model(instance)
        
        # Get changes
        changes = {}
        if not created:
            # Get previous state
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                
                # Compare fields
                for field in instance._meta.fields:
                    field_name = field.name
                    if field_name in ['id', 'created_at', 'updated_at']:
                        continue
                    
                    old_value = getattr(old_instance, field_name)
                    new_value = getattr(instance, field_name)
                    
                    if old_value != new_value:
                        changes[field_name] = {
                            'old': str(old_value),
                            'new': str(new_value)
                        }
            except:
                pass
        
        AuditLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.pk,
            object_repr=str(instance),
            changes=changes
        )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log model delete operations"""
    # Skip audit log model to avoid recursion
    if sender == AuditLog:
        return
    
    # Get current user from thread local
    try:
        from threading import local
        _thread_locals = local()
        user = getattr(_thread_locals, 'user', None)
    except:
        user = None
    
    if user:
        content_type = ContentType.objects.get_for_model(instance)
        
        AuditLog.objects.create(
            user=user,
            action='delete',
            content_type=content_type,
            object_id=instance.pk,
            object_repr=str(instance)
        )