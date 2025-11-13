"""
ASGI config for backend_salessmart project - Railway version.

Configuración simplificada sin WebSockets para Railway.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings_railway')

application = get_asgi_application()
