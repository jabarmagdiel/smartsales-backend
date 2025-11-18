"""
ASGI config for backend_salessmart project.
"""

import os
from django.core.asgi import get_asgi_application

# Usar la configuración especificada en la variable de entorno
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "backend_salessmart.settings_production"
)

# 🔥 Railway no soporta Channels sin Redis → forzamos modo simple
application = get_asgi_application()

print("🌐 ASGI inicializado en modo simple (sin Channels)")
