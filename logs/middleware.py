import logging
from django.utils.deprecation import MiddlewareMixin
from .models import LogEntry

logger = logging.getLogger(__name__)

class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Log all POST, PUT, DELETE requests for authenticated users
        if request.method in ['POST', 'PUT', 'DELETE'] and hasattr(request, 'user') and request.user.is_authenticated:
            ip = self.get_client_ip(request)
            action = f"{request.method} {request.path}"
            LogEntry.objects.create(
                ip_address=ip,
                user=request.user,
                action=action
            )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
