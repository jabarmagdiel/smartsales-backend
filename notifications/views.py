from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FCMToken, NotificationLog
from .serializers import FCMTokenSerializer, NotificationLogSerializer

class FCMTokenView(generics.CreateAPIView):
    """Vista para registrar tokens FCM"""
    serializer_class = FCMTokenSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Token FCM registrado correctamente',
                'success': True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_fcm_token(request, token):
    """Eliminar token FCM específico"""
    try:
        fcm_token = FCMToken.objects.get(token=token, user=request.user)
        fcm_token.delete()
        return Response({
            'message': 'Token FCM eliminado correctamente',
            'success': True
        }, status=status.HTTP_200_OK)
    except FCMToken.DoesNotExist:
        return Response({
            'message': 'Token no encontrado',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)

class NotificationLogListView(generics.ListAPIView):
    """Vista para listar notificaciones del usuario"""
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationLog.objects.filter(user=self.request.user)
