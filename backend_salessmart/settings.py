import os
from pathlib import Path
from datetime import timedelta

# CONFIGURACIÓN BASE
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# HOSTS Y CORS
ALLOWED_HOSTS = [
    "smartsales-backend-783403173685.europe-west1.run.app",
    ".europe-west1.run.app",
    ".run.app",
    "localhost",
    "127.0.0.1",
]



# CONFIGURACIÓN CORS SIMPLIFICADA
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configuración adicional para CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# APLICACIONES INSTALADAS
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
    'channels',  # WebSockets (opcional)
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
    'notifications',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'logs.middleware.LoggingMiddleware',
]

ROOT_URLCONF = 'backend_salessmart.urls'

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_salessmart.wsgi.application'
ASGI_APPLICATION = 'backend_salessmart.asgi.application'

# BASE DE DATOS - DESARROLLO CON SQLITE
# Configuración temporal para desarrollo local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
print("📊 Base de datos: SQLite (desarrollo local)")

# USUARIO PERSONALIZADO
AUTH_USER_MODEL = 'users.User'

# ARCHIVOS ESTÁTICOS
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WEBSOCKETS (Condicional)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT CONFIGURACIÓN
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),  # 8 horas en lugar de 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # 7 días en lugar de 1 día
    'BLACKLIST_ENABLED': True,
    'ROTATE_REFRESH_TOKENS': True,  # Rotar refresh tokens por seguridad
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'UPDATE_LAST_LOGIN': True,  # Actualizar último login
}

# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# CONFIGURACIÓN ADICIONAL
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# FIREBASE CLOUD MESSAGING
FCM_SERVER_KEY = os.environ.get('FCM_SERVER_KEY', 'TU_SERVER_KEY_AQUI')

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

print(" Configuración Django cargada")
print(f" DEBUG: {DEBUG}")
print(f" ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(" WebSockets: InMemory")
