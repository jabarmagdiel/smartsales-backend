import os
from .settings import *

# -------------------------------------------------------
# IMPORTS
# -------------------------------------------------------
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# Verificar disponibilidad de librerías de reportes
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint disponible para PDFs")
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠️ WeasyPrint no disponible - PDFs limitados")

try:
    import openpyxl
    from openpyxl import Workbook
    EXCEL_AVAILABLE = True
    print("✅ OpenPyXL disponible para Excel")
except ImportError:
    EXCEL_AVAILABLE = False
    print("⚠️ OpenPyXL no disponible - Excel limitado")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
    print("✅ ReportLab disponible para PDFs")
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab no disponible - PDFs limitados")


# -------------------------------------------------------
# DJANGO APPS CONFIGURADAS PARA PRODUCCIÓN
# -------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # External apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',

    # Local apps
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


# -------------------------------------------------------
# CONFIGURACIÓN GENERAL RAILWAY
# -------------------------------------------------------
DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-this")

ALLOWED_HOSTS = [
    ".run.app",
    "smartsales-backend-783403173685.europe-west1.run.app",
    "localhost",
    "127.0.0.1",
"*"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.run.app",
    "https://smartsales-backend-783403173685.europe-west1.run.app",
]



# -------------------------------------------------------
# TEMPLATE SETTINGS
# -------------------------------------------------------
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


# -------------------------------------------------------
# BASE DE DATOS PARA RAILWAY
# -------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # FIX de Railway: cambia postgresql:// → postgres://
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)

    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# -------------------------------------------------------
# ARCHIVOS ESTÁTICOS
# -------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# -------------------------------------------------------
# ARCHIVOS MEDIA
# -------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# -------------------------------------------------------
# CORS CONFIG PARA API Y APLICACIONES
# -------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key",
]

CORS_ALLOWED_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]


# -------------------------------------------------------
# SEGURIDAD EN PRODUCCIÓN
# -------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

if os.environ.get("RAILWAY_ENVIRONMENT") == "production":
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# -------------------------------------------------------
# JSON Web Tokens (si los usas)
# -------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

AUTH_USER_MODEL = "users.User"


# -------------------------------------------------------
# LOGGING PARA DEPURAR EN RAILWAY
# -------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


# -------------------------------------------------------
# WSGI (modo estable para producción)
# -------------------------------------------------------
WSGI_APPLICATION = "backend_salessmart.wsgi.application"

# ASGI solo si activas websockets
# ASGI_APPLICATION = "backend_salessmart.asgi.application"


# -------------------------------------------------------
# PRINTS PARA VER EN LOGS DE RAILWAY
# -------------------------------------------------------
print("🚀 Configuración Railway cargada")
print(f"🔧 DEBUG: {DEBUG}")
print(f"🗄️ Base de datos: {DATABASES['default']}")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
