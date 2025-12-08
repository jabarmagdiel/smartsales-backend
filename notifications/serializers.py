from rest_framework import serializers
from .models import FCMToken, NotificationLog

class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ['token', 'platform']
    
    def create(self, validated_data):
        # Obtener el usuario del contexto de la request
        user = self.context['request'].user
        
        # Desactivar tokens anteriores del mismo usuario y plataforma
        FCMToken.objects.filter(
            user=user, 
            platform=validated_data['platform']
        ).update(is_active=False)
        
        # Crear nuevo token
        return FCMToken.objects.create(user=user, **validated_data)

class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = '__all__'
        read_only_fields = ['user', 'sent_at']
