from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class Project(models.Model):
    """Project model"""
    STATUS_CHOICES = (
        ('planning', _('Planning')),
        ('active', _('Active')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    estimated_hours = models.DecimalField(
        _('estimated hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_hours = models.DecimalField(
        _('actual hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    budget = models.DecimalField(
        _('budget'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_cost = models.DecimalField(
        _('actual cost'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    progress = models.IntegerField(
        _('progress'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Progress percentage (0-100)')
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    team = models.ForeignKey(
        'core.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=True
    )
    is_template = models.BooleanField(_('is template'), default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subprojects'
    )
    tags = models.CharField(_('tags'), max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_projects'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Calculate progress based on tasks if not set manually
        if not self.progress and self.tasks.exists():
            total_tasks = self.tasks.count()
            completed_tasks = self.tasks.filter(status='completed').count()
            self.progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        return (
            self.end_date and 
            self.end_date < timezone.now().date() and 
            self.status not in ['completed', 'cancelled']
        )
    
    @property
    def budget_variance(self):
        """Calculate budget variance"""
        if self.budget and self.actual_cost:
            return self.actual_cost - self.budget
        return None
    
    @property
    def budget_variance_percentage(self):
        """Calculate budget variance percentage"""
        if self.budget and self.actual_cost:
            return ((self.actual_cost - self.budget) / self.budget) * 100
        return None
    
    @property
    def hours_variance(self):
        """Calculate hours variance"""
        if self.estimated_hours and self.actual_hours:
            return self.actual_hours - self.estimated_hours
        return None

class Task(models.Model):
    """Task model"""
    STATUS_CHOICES = (
        ('not_started', _('Not Started')),
        ('in_progress', _('In Progress')),
        ('blocked', _('Blocked')),
        ('completed', _('Completed')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    start_date = models.DateField(_('start date'), null=True, blank=True)
    due_date = models.DateField(_('due date'), null=True, blank=True)
    estimated_hours = models.DecimalField(
        _('estimated hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_hours = models.DecimalField(
        _('actual hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    progress = models.IntegerField(
        _('progress'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Progress percentage (0-100)')
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='dependents',
        blank=True
    )
    is_milestone = models.BooleanField(_('is milestone'), default=False)
    tags = models.CharField(_('tags'), max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Update task progress based on subtasks
        if self.subtasks.exists() and not self._state.adding:
            total_subtasks = self.subtasks.count()
            completed_subtasks = self.subtasks.filter(status='completed').count()
            self.progress = int((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0
            
            # If all subtasks are completed, mark task as completed
            if self.progress == 100 and self.status != 'completed':
                self.status = 'completed'
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        return (
            self.due_date and 
            self.due_date < timezone.now().date() and 
            self.status not in ['completed', 'blocked']
        )
    
    def check_conflicts(self):
        """Check for task conflicts"""
        conflicts = []
        
        # Check if assignee has overlapping tasks
        if self.assignee:
            overlapping_tasks = Task.objects.filter(
                assignee=self.assignee,
                status__in=['not_started', 'in_progress'],
                start_date__lte=self.due_date,
                due_date__gte=self.start_date
            ).exclude(id=self.id)
            
            for task in overlapping_tasks:
                conflicts.append({
                    'type': 'assignee_overlap',
                    'task': task,
                    'message': _('Task overlaps with another task assigned to the same person')
                })
        
        # Check if dependencies are completed
        for dependency in self.dependencies.all():
            if dependency.status != 'completed':
                conflicts.append({
                    'type': 'dependency_not_completed',
                    'task': dependency,
                    'message': _('Dependency task is not completed')
                })
        
        return conflicts

class Checklist(models.Model):
    """Checklist model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='checklists'
    )
    title = models.CharField(_('title'), max_length=255)
    is_completed = models.BooleanField(_('is completed'), default=False)
    order = models.PositiveIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Checklist')
        verbose_name_plural = _('Checklists')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.task.name} - {self.title}"

class TaskComment(models.Model):
    """Task comment model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Task Comment')
        verbose_name_plural = _('Task Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.name} - {self.author.get_full_name() if self.author else 'Unknown'}"

class TaskAttachment(models.Model):
    """Task attachment model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(_('file'), upload_to='task_attachments/')
    filename = models.CharField(_('filename'), max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Task Attachment')
        verbose_name_plural = _('Task Attachments')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.task.name} - {self.filename}"

class TaskTimeLog(models.Model):
    """Task time log model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.TextField(_('description'), blank=True)
    hours = models.DecimalField(
        _('hours'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField(_('date'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Task Time Log')
        verbose_name_plural = _('Task Time Logs')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.task.name} - {self.user.get_full_name() if self.user else 'Unknown'} - {self.hours}h"

class ProjectTemplate(models.Model):
    """Project template model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_project_templates'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Project Template')
        verbose_name_plural = _('Project Templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ProjectTemplateTask(models.Model):
    """Project template task model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ProjectTemplate,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    estimated_hours = models.DecimalField(
        _('estimated hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    is_milestone = models.BooleanField(_('is milestone'), default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks'
    )
    
    class Meta:
        verbose_name = _('Project Template Task')
        verbose_name_plural = _('Project Template Tasks')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"