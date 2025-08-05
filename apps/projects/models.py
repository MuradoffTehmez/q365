from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import User, Team

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
        blank=True
    )
    actual_hours = models.DecimalField(
        _('actual hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    budget = models.DecimalField(
        _('budget'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_cost = models.DecimalField(
        _('actual cost'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    progress = models.IntegerField(
        _('progress'),
        default=0,
        help_text=_('Progress percentage (0-100)')
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    members = models.ManyToManyField(
        User,
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
        User,
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
        blank=True
    )
    actual_hours = models.DecimalField(
        _('actual hours'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    progress = models.IntegerField(
        _('progress'),
        default=0,
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
    hours = models.DecimalField(_('hours'), max_digits=10, decimal_places=2)
    date = models.DateField(_('date'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Task Time Log')
        verbose_name_plural = _('Task Time Logs')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.task.name} - {self.user.get_full_name() if self.user else 'Unknown'} - {self.hours}h"