from django.db import models
from django.conf import settings

class FCMToken(models.Model):
    """Modelo para almacenar tokens FCM de usuarios"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.TextField(unique=True)
    platform = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications_fcm_token'
        verbose_name = 'Token FCM'
        verbose_name_plural = 'Tokens FCM'
    
    def __str__(self):
        return f'{self.user.username} - {self.platform} - {self.token[:20]}...'

class NotificationLog(models.Model):
    """Log de notificaciones enviadas"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    notification_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'notifications_log'
        verbose_name = 'Log de Notificación'
        verbose_name_plural = 'Logs de Notificaciones'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.title} - {self.sent_at}'
