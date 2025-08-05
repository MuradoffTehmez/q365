from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
import json
import uuid

class Workflow(models.Model):
    """Workflow model for defining business processes"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    model = models.CharField(
        _('model'),
        max_length=100,
        help_text=_('Model class this workflow applies to')
    )
    is_public = models.BooleanField(_('is public'), default=False)
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='allowed_workflows',
        blank=True
    )
    allowed_roles = models.ManyToManyField(
        'core.Role',
        related_name='allowed_workflows',
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_workflows'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Workflow')
        verbose_name_plural = _('Workflows')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_initial_state(self):
        """Get the initial state of this workflow"""
        return self.states.filter(is_initial=True).first()
    
    def clone(self, name=None, description=None):
        """Clone this workflow"""
        new_workflow = Workflow.objects.create(
            name=name or f"{self.name} (Copy)",
            description=description or self.description,
            model=self.model,
            status='draft',
            created_by=self.created_by
        )
        
        # Clone states
        state_mapping = {}
        for state in self.states.all():
            new_state = State.objects.create(
                workflow=new_workflow,
                name=state.name,
                description=state.description,
                is_initial=state.is_initial,
                is_final=state.is_final,
                order=state.order
            )
            state_mapping[state.id] = new_state
        
        # Clone transitions
        for transition in self.transitions.all():
            Transition.objects.create(
                workflow=new_workflow,
                name=transition.name,
                description=transition.description,
                from_state=state_mapping[transition.from_state.id],
                to_state=state_mapping[transition.to_state.id],
                conditions=transition.conditions,
                actions=transition.actions,
                order=transition.order
            )
        
        return new_workflow


class State(models.Model):
    """State model for workflow states"""
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='states'
    )
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    is_initial = models.BooleanField(_('is initial'), default=False)
    is_final = models.BooleanField(_('is final'), default=False)
    order = models.PositiveIntegerField(_('order'), default=0)
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#6c757d',
        help_text=_('Hex color code for UI representation')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')
        ordering = ['workflow', 'order']
        unique_together = ('workflow', 'name')
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one initial state per workflow
        if self.is_initial:
            State.objects.filter(
                workflow=self.workflow,
                is_initial=True
            ).exclude(id=self.id).update(is_initial=False)
        
        super().save(*args, **kwargs)


class Transition(models.Model):
    """Transition model for workflow transitions"""
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='transitions'
    )
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    from_state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='outgoing_transitions'
    )
    to_state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='incoming_transitions'
    )
    conditions = models.JSONField(
        _('conditions'),
        default=dict,
        blank=True,
        help_text=_('Conditions that must be met for this transition')
    )
    actions = models.JSONField(
        _('actions'),
        default=dict,
        blank=True,
        help_text=_('Actions to execute when this transition is taken')
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Transition')
        verbose_name_plural = _('Transitions')
        ordering = ['workflow', 'order']
        unique_together = ('workflow', 'name')
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name} ({self.from_state.name} → {self.to_state.name})"
    
    def can_transition(self, instance):
        """Check if this transition can be applied to the given instance"""
        # Check conditions
        for condition in self.conditions:
            field_path = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if not field_path or not operator:
                continue
            
            # Get field value from instance
            try:
                field_value = self._get_field_value(instance, field_path)
            except (AttributeError, IndexError, KeyError):
                return False
            
            # Apply operator
            if operator == 'equals' and field_value != value:
                return False
            elif operator == 'not_equals' and field_value == value:
                return False
            elif operator == 'contains' and value not in str(field_value):
                return False
            elif operator == 'not_contains' and value in str(field_value):
                return False
            elif operator == 'greater_than' and field_value <= value:
                return False
            elif operator == 'less_than' and field_value >= value:
                return False
            elif operator == 'greater_equal' and field_value < value:
                return False
            elif operator == 'less_equal' and field_value > value:
                return False
            elif operator == 'is_empty' and field_value:
                return False
            elif operator == 'is_not_empty' and not field_value:
                return False
        
        return True
    
    def _get_field_value(self, instance, field_path):
        """Get field value from instance using dot notation"""
        path_parts = field_path.split('.')
        value = instance
        
        for part in path_parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part)
            
            if value is None:
                break
        
        return value


class WorkflowInstance(models.Model):
    """Workflow instance model for tracking workflow execution"""
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='instances'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    current_state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='started_workflow_instances'
    )
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    data = models.JSONField(
        _('data'),
        default=dict,
        blank=True,
        help_text=_('Additional data for the workflow instance')
    )
    
    class Meta:
        verbose_name = _('Workflow Instance')
        verbose_name_plural = _('Workflow Instances')
        ordering = ['-started_at']
        unique_together = ('content_type', 'object_id')
    
    def __str__(self):
        return f"{self.workflow.name} - {self.content_object}"
    
    def get_available_transitions(self):
        """Get available transitions for the current state"""
        if not self.current_state:
            return []
        
        return self.workflow.transitions.filter(
            from_state=self.current_state
        ).order_by('order')
    
    def transition_to(self, transition, user=None):
        """Transition to a new state"""
        if not transition.can_transition(self.content_object):
            raise ValueError(_('Transition conditions not met'))
        
        # Execute actions
        for action in transition.actions:
            self._execute_action(action, user)
        
        # Update state
        self.current_state = transition.to_state
        
        # Check if workflow is completed
        if self.current_state.is_final:
            self.status = 'completed'
            self.completed_at = timezone.now()
        
        self.save()
        
        # Create history record
        WorkflowHistory.objects.create(
            workflow_instance=self,
            from_state=transition.from_state,
            to_state=transition.to_state,
            transition=transition,
            triggered_by=user,
            triggered_at=timezone.now()
        )
        
        return self
    
    def _execute_action(self, action, user=None):
        """Execute a workflow action"""
        action_type = action.get('type')
        
        if action_type == 'update_field':
            field_path = action.get('field')
            value = action.get('value')
            
            if field_path:
                self._update_field(self.content_object, field_path, value)
                self.content_object.save()
        
        elif action_type == 'send_notification':
            template = action.get('template')
            recipients = action.get('recipients', [])
            data = action.get('data', {})
            
            if template and recipients:
                self._send_notification(template, recipients, data, user)
        
        elif action_type == 'create_task':
            title = action.get('title')
            description = action.get('description', '')
            assignee_id = action.get('assignee_id')
            due_date = action.get('due_date')
            
            if title:
                self._create_task(title, description, assignee_id, due_date, user)
        
        elif action_type == 'send_email':
            template = action.get('template')
            recipients = action.get('recipients', [])
            data = action.get('data', {})
            
            if template and recipients:
                self._send_email(template, recipients, data, user)
    
    def _update_field(self, instance, field_path, value):
        """Update a field on the instance"""
        path_parts = field_path.split('.')
        target = instance
        
        # Navigate to the parent of the target field
        for part in path_parts[:-1]:
            if isinstance(target, dict):
                target = target.get(part)
            else:
                target = getattr(target, part)
            
            if target is None:
                break
        
        # Set the target field
        if target is not None:
            field_name = path_parts[-1]
            if isinstance(target, dict):
                target[field_name] = value
            else:
                setattr(target, field_name, value)
    
    def _send_notification(self, template, recipients, data, user=None):
        """Send a notification"""
        from core.models import Notification
        
        # Get recipient users
        recipient_users = []
        for recipient in recipients:
            if recipient == 'current_user' and user:
                recipient_users.append(user)
            elif recipient == 'assignee' and hasattr(self.content_object, 'assignee') and self.content_object.assignee:
                recipient_users.append(self.content_object.assignee)
            elif recipient == 'creator' and hasattr(self.content_object, 'created_by') and self.content_object.created_by:
                recipient_users.append(self.content_object.created_by)
            elif recipient == 'manager' and hasattr(self.content_object, 'manager') and self.content_object.manager:
                recipient_users.append(self.content_object.manager)
        
        # Create notifications
        for recipient_user in recipient_users:
            Notification.objects.create(
                recipient=recipient_user,
                title=data.get('title', 'Workflow Notification'),
                message=data.get('message', 'A workflow action has been triggered'),
                level=data.get('level', 'info'),
                icon=data.get('icon', 'fas fa-bell'),
                link=data.get('link', '')
            )
    
    def _create_task(self, title, description, assignee_id, due_date, user=None):
        """Create a task"""
        from projects.models import Task
        
        # Get assignee
        assignee = None
        if assignee_id:
            from core.models import User
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                pass
        
        # Create task
        Task.objects.create(
            name=title,
            description=description,
            project=getattr(self.content_object, 'project', None),
            assignee=assignee,
            due_date=due_date,
            created_by=user or self.started_by
        )
    
    def _send_email(self, template, recipients, data, user=None):
        """Send an email"""
        # This would integrate with your email system
        # For now, just log the action
        print(f"Email would be sent to {recipients} with template {template} and data {data}")


class WorkflowHistory(models.Model):
    """Workflow history model for tracking state changes"""
    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='history'
    )
    from_state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='from_history'
    )
    to_state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='to_history'
    )
    transition = models.ForeignKey(
        Transition,
        on_delete=models.CASCADE,
        related_name='history'
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_workflow_history'
    )
    triggered_at = models.DateTimeField(_('triggered at'), auto_now_add=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Workflow History')
        verbose_name_plural = _('Workflow Histories')
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.workflow_instance} - {self.from_state.name} → {self.to_state.name}"


class WorkflowTemplate(models.Model):
    """Workflow template model for reusable workflows"""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    category = models.CharField(_('category'), max_length=100, blank=True)
    model = models.CharField(
        _('model'),
        max_length=100,
        help_text=_('Model class this workflow template applies to')
    )
    workflow_data = models.JSONField(
        _('workflow data'),
        default=dict,
        help_text=_('Serialized workflow data')
    )
    is_public = models.BooleanField(_('is public'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_workflow_templates'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Workflow Template')
        verbose_name_plural = _('Workflow Templates')
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    def create_workflow(self, name=None, description=None):
        """Create a workflow from this template"""
        workflow = Workflow.objects.create(
            name=name or self.name,
            description=description or self.description,
            model=self.model,
            status='draft',
            created_by=self.created_by
        )
        
        # Create states and transitions from template data
        if self.workflow_data:
            # Create states
            state_mapping = {}
            for state_data in self.workflow_data.get('states', []):
                state = State.objects.create(
                    workflow=workflow,
                    name=state_data.get('name'),
                    description=state_data.get('description', ''),
                    is_initial=state_data.get('is_initial', False),
                    is_final=state_data.get('is_final', False),
                    order=state_data.get('order', 0),
                    color=state_data.get('color', '#6c757d')
                )
                state_mapping[state_data.get('id')] = state
            
            # Create transitions
            for transition_data in self.workflow_data.get('transitions', []):
                Transition.objects.create(
                    workflow=workflow,
                    name=transition_data.get('name'),
                    description=transition_data.get('description', ''),
                    from_state=state_mapping.get(transition_data.get('from_state_id')),
                    to_state=state_mapping.get(transition_data.get('to_state_id')),
                    conditions=transition_data.get('conditions', {}),
                    actions=transition_data.get('actions', {}),
                    order=transition_data.get('order', 0)
                )
        
        return workflow


class WorkflowTrigger(models.Model):
    """Workflow trigger model for automatic workflow execution"""
    TYPE_CHOICES = (
        ('on_create', _('On Create')),
        ('on_update', _('On Update')),
        ('on_delete', _('On Delete')),
        ('on_field_change', _('On Field Change')),
        ('scheduled', _('Scheduled')),
    )
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='triggers'
    )
    name = models.CharField(_('name'), max_length=255)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    field_name = models.CharField(
        _('field name'),
        max_length=100,
        blank=True,
        help_text=_('Field name for on_field_change triggers')
    )
    conditions = models.JSONField(
        _('conditions'),
        default=dict,
        blank=True,
        help_text=_('Conditions that must be met for this trigger')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Workflow Trigger')
        verbose_name_plural = _('Workflow Triggers')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name} ({self.get_type_display()})"
    
    def should_trigger(self, instance, old_instance=None):
        """Check if this trigger should be activated"""
        # Check conditions
        for condition in self.conditions:
            field_path = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if not field_path or not operator:
                continue
            
            # Get field value from instance
            try:
                field_value = self._get_field_value(instance, field_path)
            except (AttributeError, IndexError, KeyError):
                return False
            
            # For on_field_change triggers, check if the field actually changed
            if self.type == 'on_field_change' and old_instance:
                try:
                    old_field_value = self._get_field_value(old_instance, field_path)
                    if old_field_value == field_value:
                        continue
                except (AttributeError, IndexError, KeyError):
                    pass
            
            # Apply operator
            if operator == 'equals' and field_value != value:
                return False
            elif operator == 'not_equals' and field_value == value:
                return False
            elif operator == 'contains' and value not in str(field_value):
                return False
            elif operator == 'not_contains' and value in str(field_value):
                return False
            elif operator == 'greater_than' and field_value <= value:
                return False
            elif operator == 'less_than' and field_value >= value:
                return False
            elif operator == 'greater_equal' and field_value < value:
                return False
            elif operator == 'less_equal' and field_value > value:
                return False
            elif operator == 'is_empty' and field_value:
                return False
            elif operator == 'is_not_empty' and not field_value:
                return False
        
        return True
    
    def _get_field_value(self, instance, field_path):
        """Get field value from instance using dot notation"""
        path_parts = field_path.split('.')
        value = instance
        
        for part in path_parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part)
            
            if value is None:
                break
        
        return value


class ScheduledWorkflow(models.Model):
    """Scheduled workflow model for time-based triggers"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('running', _('Running')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    )
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='scheduled_workflows'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    schedule_type = models.CharField(
        _('schedule type'),
        max_length=20,
        choices=(
            ('once', _('Once')),
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('monthly', _('Monthly')),
            ('cron', _('Cron Expression')),
        )
    )
    scheduled_date = models.DateTimeField(_('scheduled date'))
    cron_expression = models.CharField(
        _('cron expression'),
        max_length=100,
        blank=True,
        help_text=_('Cron expression for cron-based scheduling')
    )
    parameters = models.JSONField(
        _('parameters'),
        default=dict,
        blank=True,
        help_text=_('Parameters to pass to the workflow')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    last_run = models.DateTimeField(_('last run'), null=True, blank=True)
    next_run = models.DateTimeField(_('next run'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_scheduled_workflows'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Scheduled Workflow')
        verbose_name_plural = _('Scheduled Workflows')
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"
    
    def run(self, user=None):
        """Execute the scheduled workflow"""
        # Update status
        self.status = 'running'
        self.last_run = timezone.now()
        self.save()
        
        try:
            # Create workflow instance for each matching object
            model_class = self._get_model_class(self.workflow.model)
            
            # Apply filters from parameters
            filters = self.parameters.get('filters', {})
            objects = model_class.objects.filter(**filters)
            
            for obj in objects:
                # Create workflow instance
                instance, created = WorkflowInstance.objects.get_or_create(
                    workflow=self.workflow,
                    content_type=ContentType.objects.get_for_model(obj),
                    object_id=obj.pk,
                    defaults={
                        'started_by': user or self.created_by,
                        'data': self.parameters.get('data', {})
                    }
                )
                
                # If it's a new instance, set the initial state
                if created:
                    initial_state = self.workflow.get_initial_state()
                    if initial_state:
                        instance.current_state = initial_state
                        instance.save()
            
            # Update status
            self.status = 'completed'
            
            # Schedule next run if needed
            if self.schedule_type == 'daily':
                from datetime import timedelta
                self.next_run = self.last_run + timedelta(days=1)
            elif self.schedule_type == 'weekly':
                from datetime import timedelta
                self.next_run = self.last_run + timedelta(weeks=1)
            elif self.schedule_type == 'monthly':
                from datetime import timedelta
                self.next_run = self.last_run + timedelta(days=30)
            
            self.save()
            
        except Exception as e:
            # Update status
            self.status = 'failed'
            self.save()
            
            # Log the error
            print(f"Error running scheduled workflow {self.id}: {str(e)}")
            raise e
    
    def _get_model_class(self, model_path):
        """Get model class from string path"""
        app_label, model_name = model_path.split('.')
        from django.apps import apps
        return apps.get_model(app_label, model_name)