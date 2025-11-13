import os
from .settings import *

# Importar dj_database_url solo si está disponible
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# Sobrescribir INSTALLED_APPS sin channels para Railway
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    # 'channels',  # Deshabilitado para Railway
    'drf_yasg',

    'products',
    'users',
    'sales',
    'logistics',
    'posventa',
    'logs',
    'reportes',
    'ia',
    'reports',
]

# Configuración de producción para Railway
DEBUG = False

# Configuración de seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# Hosts permitidos para Railway
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# Configuración de base de datos para Railway
# Railway proporciona DATABASE_URL automáticamente
if 'DATABASE_URL' in os.environ and HAS_DJ_DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Configuración de archivos estáticos para Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise para servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de CORS para Railway
CORS_ALLOWED_ORIGINS = [
    # Frontend Web (Vercel u otro)
    os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    
    # Para desarrollo local
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Para aplicación móvil
CORS_ALLOW_ALL_ORIGINS = True

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
    'x-api-key',
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

# Configuración de seguridad para Railway
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Solo activar HTTPS en producción real
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Configuración de sesiones
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Configuración de logging para Railway
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

# Configuración de cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configuración de email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración de timezone
USE_TZ = True
TIME_ZONE = 'UTC'

# Configuración de internacionalización
LANGUAGE_CODE = 'es-es'
USE_I18N = True
USE_L10N = True

# Configuración WSGI para Railway (más estable)
WSGI_APPLICATION = 'backend_salessmart.wsgi.application'

# WebSockets deshabilitados temporalmente para Railway
# Descomentar cuando agregues Redis
# ASGI_APPLICATION = 'backend_salessmart.asgi.application'
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer',
#     }
# }

# En producción, usar Redis si está disponible
# if 'REDIS_URL' in os.environ:
#     CHANNEL_LAYERS = {
#         'default': {
#             'BACKEND': 'channels_redis.core.RedisChannelLayer',
#             'CONFIG': {
#                 "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
#             },
#         },
#     }

print(f"🚀 Configuración de Railway cargada")
print(f"🔧 DEBUG: {DEBUG}")
print(f"🗄️ Base de datos: {'PostgreSQL (Railway)' if 'DATABASE_URL' in os.environ else 'SQLite (desarrollo)'}")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"📡 WebSockets: {'Redis' if 'REDIS_URL' in os.environ else 'InMemory'}")
