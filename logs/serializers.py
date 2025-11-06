from rest_framework import serializers
from .models import LogEntry

class LogEntrySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = LogEntry
        fields = ['id', 'ip_address', 'user', 'user_username', 'timestamp', 'action']
