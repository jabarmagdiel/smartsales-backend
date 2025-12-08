import json
import requests
from django.conf import settings
from django.contrib.auth.models import User
from .models import FCMToken, NotificationLog

class NotificationService:
    """Servicio para enviar notificaciones push usando Firebase Cloud Messaging"""
    
    FCM_URL = "https://fcm.googleapis.com/fcm/send"
    
    @classmethod
    def send_notification(cls, user_id, title, body, data=None, notification_type='general'):
        """
        Enviar notificación push a un usuario específico
        
        Args:
            user_id: ID del usuario
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (dict)
            notification_type: Tipo de notificación
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Obtener tokens FCM activos del usuario
            fcm_tokens = FCMToken.objects.filter(user=user, is_active=True)
            
            if not fcm_tokens.exists():
                print(f"⚠️ Usuario {user.username} no tiene tokens FCM activos")
                return False
            
            # Preparar datos de la notificación
            if data is None:
                data = {}
            
            data.update({
                'type': notification_type,
                'user_id': str(user_id),
                'timestamp': str(int(time.time()))
            })
            
            success_count = 0
            
            # Enviar a todos los tokens del usuario
            for fcm_token in fcm_tokens:
                success = cls._send_to_token(
                    token=fcm_token.token,
                    title=title,
                    body=body,
                    data=data
                )
                
                if success:
                    success_count += 1
                else:
                    # Desactivar token si falla
                    fcm_token.is_active = False
                    fcm_token.save()
            
            # Registrar en log
            NotificationLog.objects.create(
                user=user,
                title=title,
                body=body,
                data=data,
                notification_type=notification_type,
                success=success_count > 0
            )
            
            return success_count > 0
            
        except User.DoesNotExist:
            print(f"❌ Usuario con ID {user_id} no existe")
            return False
        except Exception as e:
            print(f"❌ Error enviando notificación: {e}")
            return False
    
    @classmethod
    def _send_to_token(cls, token, title, body, data):
        """Enviar notificación a un token específico"""
        try:
            # Obtener server key de Firebase (debe estar en settings)
            server_key = getattr(settings, 'FCM_SERVER_KEY', None)
            
            if not server_key:
                print("❌ FCM_SERVER_KEY no configurado en settings")
                return False
            
            headers = {
                'Authorization': f'key={server_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'to': token,
                'notification': {
                    'title': title,
                    'body': body,
                    'icon': 'ic_launcher',
                    'sound': 'default',
                    'color': '#00BCD4'  # Color primario de la app
                },
                'data': data,
                'priority': 'high'
            }
            
            response = requests.post(
                cls.FCM_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', 0) > 0:
                    print(f"✅ Notificación enviada exitosamente")
                    return True
                else:
                    print(f"❌ Error en FCM: {result}")
                    return False
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando a token: {e}")
            return False
    
    @classmethod
    def send_order_notification(cls, user_id, order_id, status, message=None):
        """Enviar notificación específica de pedido"""
        
        status_messages = {
            'confirmed': 'Tu pedido ha sido confirmado',
            'preparing': 'Tu pedido se está preparando',
            'shipped': 'Tu pedido ha sido enviado',
            'delivered': 'Tu pedido ha sido entregado',
            'cancelled': 'Tu pedido ha sido cancelado'
        }
        
        title = "Estado de tu pedido"
        body = message or status_messages.get(status, f"Tu pedido #{order_id} ha cambiado de estado")
        
        data = {
            'order_id': str(order_id),
            'status': status,
            'type': 'order_status_changed'
        }
        
        return cls.send_notification(
            user_id=user_id,
            title=title,
            body=body,
            data=data,
            notification_type='order_status'
        )
    
    @classmethod
    def send_payment_notification(cls, user_id, order_id, payment_status):
        """Enviar notificación de pago"""
        
        if payment_status == 'confirmed':
            title = "Pago confirmado"
            body = f"El pago de tu pedido #{order_id} ha sido confirmado"
        elif payment_status == 'failed':
            title = "Pago fallido"
            body = f"Hubo un problema con el pago de tu pedido #{order_id}"
        else:
            title = "Estado de pago"
            body = f"El estado de pago de tu pedido #{order_id} ha cambiado"
        
        data = {
            'order_id': str(order_id),
            'payment_status': payment_status,
            'type': 'payment_status'
        }
        
        return cls.send_notification(
            user_id=user_id,
            title=title,
            body=body,
            data=data,
            notification_type='payment'
        )

# Importar time al inicio del archivo
import time
