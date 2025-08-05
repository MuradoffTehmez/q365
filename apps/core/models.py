from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User model with additional fields"""
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        )]
    )
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    position = models.CharField(_('position'), max_length=100, blank=True, null=True)
    employee_id = models.CharField(_('employee ID'), max_length=20, blank=True, null=True, unique=True)
    is_active_employee = models.BooleanField(_('is active employee'), default=True)
    hire_date = models.DateField(_('hire date'), blank=True, null=True)
    termination_date = models.DateField(_('termination date'), blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return self.get_full_name() or self.username


class Role(models.Model):
    """Role model for role-based access control"""
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    permissions = models.ManyToManyField(
        'Permission',
        verbose_name=_('permissions'),
        blank=True,
        related_name='roles'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """Custom permission model for fine-grained access control"""
    name = models.CharField(_('name'), max_length=100)
    codename = models.CharField(_('codename'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """User-Role relationship model"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user} - {self.role}"


class Organization(models.Model):
    """Top-level organization model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    address = models.TextField(_('address'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    website = models.URLField(_('website'), blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    logo = models.ImageField(_('logo'), upload_to='organization_logos/', blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Department model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        unique_together = ('organization', 'code')
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Sector(models.Model):
    """Sector model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='sectors'
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_sectors'
    )
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sector')
        verbose_name_plural = _('Sectors')
        unique_together = ('department', 'code')
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Team(models.Model):
    """Team model"""
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20)
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )
    members = models.ManyToManyField(
        User,
        related_name='teams',
        blank=True
    )
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        unique_together = ('sector', 'code')
    
    def __str__(self):
        return f"{self.sector.name} - {self.name}"


class Notification(models.Model):
    """Notification model"""
    LEVEL_CHOICES = (
        ('info', _('Info')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    level = models.CharField(
        _('level'),
        max_length=10,
        choices=LEVEL_CHOICES,
        default='info'
    )
    is_read = models.BooleanField(_('is read'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    link = models.URLField(_('link'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient} - {self.title}"


class Reminder(models.Model):
    """Reminder model"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    remind_at = models.DateTimeField(_('remind at'))
    is_completed = models.BooleanField(_('is completed'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    link = models.URLField(_('link'), blank=True)
    
    class Meta:
        verbose_name = _('Reminder')
        verbose_name_plural = _('Reminders')
        ordering = ['remind_at']
    
    def __str__(self):
        return f"{self.user} - {self.title}"