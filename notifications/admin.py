from django.contrib import admin
from .models import FCMToken, NotificationLog

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'token_preview', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['created_at', 'updated_at']
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..." if obj.token else ""
    token_preview.short_description = "Token (Preview)"

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'success', 'sent_at']
    list_filter = ['notification_type', 'success', 'sent_at']
    search_fields = ['user__username', 'title', 'body']
    readonly_fields = ['sent_at']
    
    def has_add_permission(self, request):
        return False  # No permitir crear logs manualmente
