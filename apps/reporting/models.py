from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import User, Organization

class Report(models.Model):
    """Report model"""
    TYPE_CHOICES = (
        ('table', _('Table')),
        ('chart', _('Chart')),
        ('pivot', _('Pivot')),
        ('dashboard', _('Dashboard')),
    )
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('archived', _('Archived')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    query = models.TextField(_('query'), blank=True)
    config = models.JSONField(_('config'), default=dict, blank=True)
    is_public = models.BooleanField(_('is public'), default=False)
    allowed_users = models.ManyToManyField(
        User,
        related_name='allowed_reports',
        blank=True
    )
    allowed_roles = models.ManyToManyField(
        'core.Role',
        related_name='allowed_reports',
        blank=True
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_reports'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Dashboard(models.Model):
    """Dashboard model"""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    layout = models.JSONField(_('layout'), default=dict, blank=True)
    is_public = models.BooleanField(_('is public'), default=False)
    allowed_users = models.ManyToManyField(
        User,
        related_name='allowed_dashboards',
        blank=True
    )
    allowed_roles = models.ManyToManyField(
        'core.Role',
        related_name='allowed_dashboards',
        blank=True
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='dashboards'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_dashboards'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboards')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """Dashboard widget model"""
    TYPE_CHOICES = (
        ('report', _('Report')),
        ('kpi', _('KPI')),
        ('chart', _('Chart')),
        ('html', _('HTML')),
    )
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    title = models.CharField(_('title'), max_length=255)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    config = models.JSONField(_('config'), default=dict, blank=True)
    position_x = models.IntegerField(_('position X'), default=0)
    position_y = models.IntegerField(_('position Y'), default=0)
    width = models.IntegerField(_('width'), default=4)
    height = models.IntegerField(_('height'), default=4)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgets')
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class KPI(models.Model):
    """KPI model"""
    TYPE_CHOICES = (
        ('number', _('Number')),
        ('percentage', _('Percentage')),
        ('currency', _('Currency')),
        ('duration', _('Duration')),
    )
    
    AGGREGATION_CHOICES = (
        ('sum', _('Sum')),
        ('average', _('Average')),
        ('count', _('Count')),
        ('min', _('Min')),
        ('max', _('Max')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    model = models.CharField(_('model'), max_length=100)
    field = models.CharField(_('field'), max_length=100)
    aggregation = models.CharField(
        _('aggregation'),
        max_length=20,
        choices=AGGREGATION_CHOICES
    )
    filters = models.JSONField(_('filters'), default=dict, blank=True)
    target = models.DecimalField(
        _('target'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    unit = models.CharField(_('unit'), max_length=20, blank=True)
    is_public = models.BooleanField(_('is public'), default=False)
    allowed_users = models.ManyToManyField(
        User,
        related_name='allowed_kpis',
        blank=True
    )
    allowed_roles = models.ManyToManyField(
        'core.Role',
        related_name='allowed_kpis',
        blank=True
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='kpis'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_kpis'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('KPI')
        verbose_name_plural = _('KPIs')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ScheduledReport(models.Model):
    """Scheduled report model"""
    FREQUENCY_CHOICES = (
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    )
    
    FORMAT_CHOICES = (
        ('pdf', _('PDF')),
        ('excel', _('Excel')),
        ('csv', _('CSV')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='scheduled_reports'
    )
    frequency = models.CharField(
        _('frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES
    )
    format = models.CharField(
        _('format'),
        max_length=10,
        choices=FORMAT_CHOICES
    )
    recipients = models.ManyToManyField(
        User,
        related_name='scheduled_reports'
    )
    additional_emails = models.TextField(_('additional emails'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    next_run = models.DateTimeField(_('next run'), null=True, blank=True)
    last_run = models.DateTimeField(_('last run'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_scheduled_reports'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Scheduled Report')
        verbose_name_plural = _('Scheduled Reports')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.report.name}"