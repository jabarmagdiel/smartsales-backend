from django.db import models
from users.models import User

class LogEntry(models.Model):
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs_activity_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.TextField()

    def get_client_ip(self, request):
        """Obtiene la IP del cliente, considerando proxies (como Daphne)."""
        # X-Forwarded-For es común si estás detrás de un proxy/load balancer
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            # Usa REMOTE_ADDR como fallback
            ip = request.META.get('REMOTE_ADDR', 'IP_UNKNOWN')
        self.ip_address = ip

    def __str__(self):
        return f"{self.timestamp} - {self.user.username if self.user else 'Anonymous'} - {self.action}"
