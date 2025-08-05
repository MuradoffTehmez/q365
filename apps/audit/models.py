from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class AuditLog(models.Model):
    """Audit log model"""
    ACTION_CHOICES = (
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('other', _('Other')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(
        _('action'),
        max_length=10,
        choices=ACTION_CHOICES
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(_('object representation'), max_length=255, blank=True)
    changes = models.JSONField(_('changes'), default=dict, blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} {self.action} {self.object_repr} at {self.timestamp}"