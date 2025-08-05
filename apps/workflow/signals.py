from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import WorkflowInstance, WorkflowTrigger


@receiver(post_save)
def handle_workflow_triggers(sender, instance, created, **kwargs):
    """Handle workflow triggers on model save"""
    # Skip workflow models to avoid recursion
    if sender._meta.app_label == 'workflow':
        return
    
    # Get content type for the model
    try:
        content_type = ContentType.objects.get_for_model(sender)
    except ContentType.DoesNotExist:
        return
    
    # Get active triggers for this model
    triggers = WorkflowTrigger.objects.filter(
        workflow__model=f"{content_type.app_label}.{content_type.model}",
        is_active=True
    )
    
    # Check each trigger
    for trigger in triggers:
        # Get old instance for update triggers
        old_instance = None
        if not created and trigger.type in ['on_update', 'on_field_change']:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                continue
        
        # Check if trigger should be activated
        if trigger.should_trigger(instance, old_instance):
            # Start workflow for the object
            WorkflowInstance.objects.get_or_create(
                workflow=trigger.workflow,
                content_type=content_type,
                object_id=instance.pk,
                defaults={
                    'started_by': instance.created_by if hasattr(instance, 'created_by') else None
                }
            )


@receiver(post_delete)
def handle_delete_workflow_triggers(sender, instance, **kwargs):
    """Handle workflow triggers on model delete"""
    # Skip workflow models to avoid recursion
    if sender._meta.app_label == 'workflow':
        return
    
    # Get content type for the model
    try:
        content_type = ContentType.objects.get_for_model(sender)
    except ContentType.DoesNotExist:
        return
    
    # Get active on_delete triggers for this model
    triggers = WorkflowTrigger.objects.filter(
        workflow__model=f"{content_type.app_label}.{content_type.model}",
        type='on_delete',
        is_active=True
    )
    
    # Check each trigger
    for trigger in triggers:
        # Check if trigger should be activated
        if trigger.should_trigger(instance):
            # Start workflow for the object
            WorkflowInstance.objects.get_or_create(
                workflow=trigger.workflow,
                content_type=content_type,
                object_id=instance.pk,
                defaults={
                    'started_by': instance.created_by if hasattr(instance, 'created_by') else None
                }
            )