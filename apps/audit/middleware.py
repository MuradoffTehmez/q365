import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to log user actions"""
    
    def process_request(self, request):
        """Process request to get IP and user agent"""
        request.ip_address = self.get_client_ip(request)
        request.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Store user in thread local for signals
        try:
            from threading import local
            _thread_locals = local()
            _thread_locals.user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        except:
            pass
        
        return None
    
    def process_response(self, request, response):
        """Process response to log actions"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Log login/logout actions
            if request.path == '/api/token/' and response.status_code == 200:
                self.log_action(request, 'login')
            elif request.path == '/api/token/logout/' and response.status_code == 200:
                self.log_action(request, 'logout')
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_action(self, request, action, obj=None, changes=None):
        """Log user action"""
        content_type = None
        object_id = None
        object_repr = ''
        
        if obj:
            content_type = ContentType.objects.get_for_model(obj)
            object_id = obj.pk
            object_repr = str(obj)
        
        AuditLog.objects.create(
            user=request.user,
            action=action,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes or {},
            ip_address=request.ip_address,
            user_agent=request.user_agent
        )