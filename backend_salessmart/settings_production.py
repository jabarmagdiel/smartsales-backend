import os
from .settings import *

# Configuración de producción para Google Cloud
DEBUG = False

# Obtener PROJECT_ID de las variables de entorno
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')

# Función simplificada para obtener configuración
def get_config(key, default=None):
    """Obtener configuración de variables de entorno"""
    return os.environ.get(key, default)

# Configuración de seguridad - Usar variable de entorno directamente
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# Configuraciones ya importadas de settings.py

# Hosts permitidos
ALLOWED_HOSTS = [
    '.run.app',  # Dominios de Cloud Run
    '.googleapis.com',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Configuración de base de datos se define al final del archivo

# Configuración de CORS para WEB y MÓVIL
CORS_ALLOWED_ORIGINS = [
    # Frontend Web (Next.js) - Todas las posibles URLs
    "https://smartsales-frontend.vercel.app",
    "https://smartsales-frontend-git-main-miguels-projects.vercel.app", 
    "https://smartsales-frontend-miguels-projects.vercel.app",
    "https://nueva-version-smartsales-frontend.vercel.app",
    "https://smartsales-backend-783403173685.europe-west1.run.app",
    
    # Desarrollo local
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Para aplicación móvil, permitir todos los orígenes
CORS_ALLOW_ALL_ORIGINS = True  # Necesario para aplicaciones móviles
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

# Configuración de sesiones - Relajada para desarrollo
SESSION_COOKIE_SECURE = False  # Cambiar a False para permitir HTTP
CSRF_COOKIE_SECURE = False     # Cambiar a False para permitir HTTP
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False   # Cambiar a False para APIs

# Configuración CSRF adicional
CSRF_TRUSTED_ORIGINS = [
    "https://smartsales-backend-783403173685.europe-west1.run.app",
    "https://*.europe-west1.run.app",
    "https://*.run.app",
]

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

# Configuración de WebSockets (para notificaciones en tiempo real)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ASGI Application
ASGI_APPLICATION = 'backend_salessmart.asgi.application'

# FORZAR PostgreSQL - SOBRESCRIBIR cualquier configuración anterior
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

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
#  ARCHIVOS ESTÁTICOS PARA PRODUCCIÓN (WhiteNoise)
# ============================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)


# ============================================================
#  CONFIGURACIÓN DE MEDIA - GOOGLE CLOUD STORAGE O LOCAL
# ============================================================

# Verificar si Google Cloud Storage está disponible
USE_CLOUD_STORAGE = get_config('USE_CLOUD_STORAGE', 'false').lower() == 'true'

if USE_CLOUD_STORAGE:
    # Configuración de Google Cloud Storage
    try:
        DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
        GS_BUCKET_NAME = get_config('GS_BUCKET_NAME', 'smartsales-media')
        GS_DEFAULT_ACL = "publicRead"
        MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
        MEDIA_ROOT = None
        print("📁 Usando Google Cloud Storage para media")
    except Exception as e:
        print(f"⚠️ Error configurando Google Cloud Storage: {e}")
        USE_CLOUD_STORAGE = False

if not USE_CLOUD_STORAGE:
    # Configuración local para media
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    print("📁 Usando almacenamiento local para media")


# ============================================================
#  DEBUG DESACTIVADO EN PRODUCCIÓN
# ============================================================

DEBUG = False


# ============================================================
#  MOSTRAR CONFIGURACIÓN EN LOGS (Opcional)
# ============================================================

print("🚀 Configuración de producción cargada")
print(f"🔧 DEBUG: {DEBUG}")
print(f"🗄️ Base de datos: PostgreSQL (Cloud SQL)")
print(f"📁 MEDIA_URL: {MEDIA_URL}")
