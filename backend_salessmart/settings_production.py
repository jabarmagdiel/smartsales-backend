import os
from .settings import *

# Configuración de producción para Google Cloud
DEBUG = False

# Obtener PROJECT_ID de las variables de entorno
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')

# Función para obtener secretos de Google Secret Manager
def get_secret(secret_name):
    """Obtener secreto de Google Secret Manager"""
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error obteniendo secreto {secret_name}: {e}")
        # Fallback a variables de entorno para desarrollo
        return os.environ.get(secret_name.upper().replace('-', '_'))

# Configuración de seguridad
SECRET_KEY = get_secret('django-secret-key') or 'fallback-secret-key-for-development'

# Hosts permitidos
ALLOWED_HOSTS = [
    '.run.app',  # Dominios de Cloud Run
    '.googleapis.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Configuración de base de datos para Cloud SQL
# SIEMPRE usar PostgreSQL en settings_production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'smartsales_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'KellyDuran2210*'),
        'HOST': os.environ.get('DB_HOST', '34.38.132.155'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de CORS para WEB y MÓVIL
CORS_ALLOWED_ORIGINS = [
    # Backend propio (para Railway frontend)
    "https://smartsales-backend-783403173685.europe-west1.run.app",
    
    # Frontend Web (Next.js)
    "https://smartsales-frontend.vercel.app",  # Reemplazar con tu dominio frontend
    "http://localhost:3000",  # Desarrollo local web
    "http://127.0.0.1:3000",
    
    # Para desarrollo local
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Para aplicación móvil, permitir todos los orígenes
# Las apps móviles no siempre envían Origin header correctamente
CORS_ALLOW_ALL_ORIGINS = True  # Necesario para aplicaciones móviles

# Configuración específica para móviles
CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400

# Headers adicionales para móvil
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-api-key',  # Para móvil
]

# Métodos permitidos para API REST
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Configuración adicional de CORS
CORS_ALLOW_CREDENTIALS = True

# Configuración de seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuración de sesiones
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Configuración de logging para Cloud Run
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'backend_salessmart': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuración de cache (opcional, para mejor performance)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configuración de email (opcional)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración de timezone
USE_TZ = True
TIME_ZONE = 'UTC'

# Configuración de internacionalización
LANGUAGE_CODE = 'es-es'
USE_I18N = True
USE_L10N = True

print(f"🚀 Configuración de producción cargada para proyecto: {PROJECT_ID}")
print(f"🔧 DEBUG: {DEBUG}")
print(f"🗄️ Base de datos: {'Cloud SQL' if os.environ.get('GAE_APPLICATION') else 'SQLite (desarrollo)'}")
