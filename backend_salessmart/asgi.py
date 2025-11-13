"""
ASGI config for backend_salessmart project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings_railway')

django.setup()

# Verificar si channels está disponible
try:
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from django.urls import path
    from sales.consumers import OrderConsumer, NotificationConsumer
    
    django_asgi_app = get_asgi_application()
    
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter([
                path('ws/orders/', OrderConsumer.as_asgi()),
                path('ws/notificaciones/', NotificationConsumer.as_asgi()),
            ]),
        ),
    })
    print("🔌 WebSockets habilitados con Channels")
    
except ImportError:
    # Fallback para Railway sin channels
    application = get_asgi_application()
    print("🌐 Modo ASGI simple sin WebSockets")
