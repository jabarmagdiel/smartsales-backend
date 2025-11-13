"""
ASGI config for backend_salessmart project.
"""

import os
from django.core.asgi import get_asgi_application

# Usar SIEMPRE settings_railway para producción en Railway
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "backend_salessmart.settings_railway"
)

# 🔥 Railway no soporta Channels sin Redis → forzamos modo simple
application = get_asgi_application()

print("🌐 ASGI inicializado en modo simple (sin Channels)")
