from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class ServiceTicket(models.Model):
    """Service ticket model"""
    STATUS_CHOICES = (
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('waiting_on_customer', _('Waiting on Customer')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    TYPE_CHOICES = (
        ('technical', _('Technical')),
        ('billing', _('Billing')),
        ('feature_request', _('Feature Request')),
        ('other', _('Other')),
    )
    
    IMPACT_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    status = models.CharField(
        _('status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default='new'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='technical'
    )
    impact = models.CharField(
        _('impact'),
        max_length=20,
        choices=IMPACT_CHOICES,
        default='medium'
    )
    customer = models.ForeignKey(
        'crm.Customer',
        on_delete=models.CASCADE,
        related_name='service_tickets'
    )
    contact = models.ForeignKey(
        'crm.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_service_tickets'
    )
    team = models.ForeignKey(
        'core.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_tickets'
    )
    sla = models.ForeignKey(
        'SLA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_tickets'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_service_tickets'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    closed_at = models.DateTimeField(_('closed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Service Ticket')
        verbose_name_plural = _('Service Tickets')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"#{self.id} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Update resolved_at and closed_at timestamps
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved' and self.resolved_at:
            self.resolved_at = None
            
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.status != 'closed' and self.closed_at:
            self.closed_at = None
            
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if ticket is overdue based on SLA"""
        if not self.sla or self.status in ['resolved', 'closed']:
            return False
        
        # Calculate due time based on SLA
        if self.sla.business_hours_only:
            # This would require business hours calculation
            # For simplicity, we'll use a basic calculation
            due_time = self.created_at + self.sla.resolution_time
        else:
            due_time = self.created_at + self.sla.resolution_time
        
        return timezone.now() > due_time
    
    @property
    def time_to_resolve(self):
        """Calculate time to resolve based on SLA"""
        if not self.sla or self.status in ['resolved', 'closed']:
            return None
        
        if self.sla.business_hours_only:
            # This would require business hours calculation
            # For simplicity, we'll use a basic calculation
            due_time = self.created_at + self.sla.resolution_time
        else:
            due_time = self.created_at + self.sla.resolution_time
        
        remaining = due_time - timezone.now()
        return remaining.total_seconds() if remaining.total_seconds() > 0 else 0

class TicketComment(models.Model):
    """Ticket comment model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        ServiceTicket,
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
    is_internal = models.BooleanField(_('is internal'), default=False)
    is_private = models.BooleanField(_('is private'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ticket Comment')
        verbose_name_plural = _('Ticket Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment on #{self.ticket.id} by {self.author.get_full_name() if self.author else 'Unknown'}"

class TicketAttachment(models.Model):
    """Ticket attachment model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        ServiceTicket,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(_('file'), upload_to='ticket_attachments/')
    filename = models.CharField(_('filename'), max_length=255)
    file_size = models.PositiveIntegerField(_('file size'), default=0)
    content_type = models.CharField(_('content type'), max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ticket Attachment')
        verbose_name_plural = _('Ticket Attachments')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - Ticket #{self.ticket.id}"
    
    def save(self, *args, **kwargs):
        # Set file size and content type
        if self.file:
            self.file_size = self.file.size
            self.content_type = self.file.content_type or 'application/octet-stream'
        
        super().save(*args, **kwargs)

class TicketTimeLog(models.Model):
    """Ticket time log model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        ServiceTicket,
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
    billable = models.BooleanField(_('billable'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ticket Time Log')
        verbose_name_plural = _('Ticket Time Logs')
        ordering = ['-date']
    
    def __str__(self):
        return f"#{self.ticket.id} - {self.user.get_full_name() if self.user else 'Unknown'} - {self.hours}h"

class RMA(models.Model):
    """RMA (Return Merchandise Authorization) model"""
    STATUS_CHOICES = (
        ('requested', _('Requested')),
        ('approved', _('Approved')),
        ('received', _('Received')),
        ('diagnosing', _('Diagnosing')),
        ('repairing', _('Repairing')),
        ('repaired', _('Repaired')),
        ('replaced', _('Replaced')),
        ('shipped', _('Shipped')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        ServiceTicket,
        on_delete=models.CASCADE,
        related_name='rmas'
    )
    rma_number = models.CharField(_('RMA number'), max_length=50, unique=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested'
    )
    product_name = models.CharField(_('product name'), max_length=255)
    serial_number = models.CharField(_('serial number'), max_length=100, blank=True)
    reason = models.TextField(_('reason'))
    diagnosis = models.TextField(_('diagnosis'), blank=True)
    resolution = models.TextField(_('resolution'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_rmas'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('RMA')
        verbose_name_plural = _('RMAs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rma_number} - {self.product_name}"

class ServiceCall(models.Model):
    """Service call model"""
    STATUS_CHOICES = (
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        ServiceTicket,
        on_delete=models.CASCADE,
        related_name='service_calls'
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    scheduled_date = models.DateTimeField(_('scheduled date'))
    duration = models.DurationField(_('duration'), null=True, blank=True)
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_calls'
    )
    address = models.TextField(_('address'))
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_service_calls'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Service Call')
        verbose_name_plural = _('Service Calls')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"

class ServicePlan(models.Model):
    """Service plan model"""
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('cancelled', _('Cancelled')),
    )
    
    TYPE_CHOICES = (
        ('maintenance', _('Maintenance')),
        ('support', _('Support')),
        ('warranty', _('Warranty')),
        ('sla', _('SLA')),
        ('other', _('Other')),
    )
    
    FREQUENCY_CHOICES = (
        ('one_time', _('One Time')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'crm.Customer',
        on_delete=models.CASCADE,
        related_name='service_plans'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='maintenance'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    frequency = models.CharField(
        _('frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='one_time'
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    price = models.DecimalField(
        _('price'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    auto_renew = models.BooleanField(_('auto renew'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_service_plans'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Service Plan')
        verbose_name_plural = _('Service Plans')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"
    
    @property
    def is_expired(self):
        """Check if service plan is expired"""
        return self.end_date < timezone.now().date()

class SLA(models.Model):
    """SLA (Service Level Agreement) model"""
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES
    )
    response_time = models.DurationField(_('response time'))
    resolution_time = models.DurationField(_('resolution time'))
    business_hours_only = models.BooleanField(_('business hours only'), default=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('SLA')
        verbose_name_plural = _('SLAs')
        ordering = ['priority']
    
    def __str__(self):
        return self.name

class Region(models.Model):
    """Region model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Zone(models.Model):
    """Zone model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='zones'
    )
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Zone')
        verbose_name_plural = _('Zones')
        ordering = ['name']
        unique_together = ('region', 'code')
    
    def __str__(self):
        return f"{self.region.name} - {self.name}"

class Skill(models.Model):
    """Skill model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    category = models.CharField(_('category'), max_length=100, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TechnicianSkill(models.Model):
    """Technician skill model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='technicians'
    )
    proficiency_level = models.IntegerField(
        _('proficiency level'),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Proficiency level (1-5)')
    )
    certified = models.BooleanField(_('certified'), default=False)
    certification_date = models.DateField(_('certification date'), null=True, blank=True)
    certification_expiry = models.DateField(_('certification expiry'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Technician Skill')
        verbose_name_plural = _('Technician Skills')
        unique_together = ('technician', 'skill')
    
    def __str__(self):
        return f"{self.technician.get_full_name()} - {self.skill.name}"
    
    @property
    def is_certification_expired(self):
        """Check if certification is expired"""
        return (
            self.certification_expiry and 
            self.certification_expiry < timezone.now().date()
        )