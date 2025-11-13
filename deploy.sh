#!/bin/bash

# 🚀 Script de despliegue automático para SmartSales Backend en Google Cloud

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "Este script debe ejecutarse desde el directorio del backend (donde está manage.py)"
    exit 1
fi

# Obtener PROJECT_ID de gcloud
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    print_error "No se pudo obtener el PROJECT_ID. Ejecuta: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_message "Desplegando SmartSales Backend en proyecto: $PROJECT_ID"

# Paso 1: Verificar dependencias
print_message "Verificando dependencias..."

if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK no está instalado"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi

print_success "Dependencias verificadas"

# Paso 2: Habilitar APIs necesarias
print_message "Habilitando APIs necesarias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
print_success "APIs habilitadas"

# Paso 3: Crear secretos si no existen
print_message "Configurando secretos..."

# Django Secret Key
if ! gcloud secrets describe django-secret-key &>/dev/null; then
    print_message "Creando Django secret key..."
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" | \
    gcloud secrets create django-secret-key --data-file=-
    print_success "Django secret key creado"
else
    print_warning "Django secret key ya existe"
fi

# Paso 4: Construir y subir imagen
print_message "Construyendo imagen Docker..."
IMAGE_NAME="gcr.io/$PROJECT_ID/smartsales-backend"

# Usar requirements de producción
cp requirements-production.txt requirements.txt

gcloud builds submit --tag $IMAGE_NAME
print_success "Imagen construida y subida: $IMAGE_NAME"

# Paso 5: Desplegar en Cloud Run
print_message "Desplegando en Cloud Run..."

SERVICE_NAME="smartsales-backend"
REGION="us-central1"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --set-env-vars DJANGO_SETTINGS_MODULE=backend_salessmart.settings_production \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --timeout 300

print_success "Servicio desplegado en Cloud Run"

# Paso 6: Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
print_success "Servicio disponible en: $SERVICE_URL"

# Paso 7: Ejecutar migraciones (opcional)
print_message "¿Deseas ejecutar las migraciones de Django? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    print_message "Ejecutando migraciones..."
    gcloud run jobs create django-migrate \
        --image $IMAGE_NAME \
        --region $REGION \
        --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
        --set-env-vars DJANGO_SETTINGS_MODULE=backend_salessmart.settings_production \
        --command python \
        --args manage.py,migrate \
        --memory 1Gi \
        --cpu 1 \
        --max-retries 3 \
        --parallelism 1 \
        --task-count 1
    
    gcloud run jobs execute django-migrate --region $REGION --wait
    print_success "Migraciones ejecutadas"
fi

# Paso 8: Verificar despliegue
print_message "Verificando despliegue..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/v1/productos/" || echo "000")

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "401" ]; then
    print_success "✅ Despliegue exitoso!"
    echo ""
    echo "🌐 URL del servicio: $SERVICE_URL"
    echo "🔧 Panel de admin: $SERVICE_URL/admin/"
    echo "📊 API: $SERVICE_URL/api/v1/"
    echo ""
    echo "📱 Actualiza la configuración en tu app móvil:"
    echo "   lib/core/config/api_config.dart"
    echo "   baseUrl = '$SERVICE_URL';"
    echo ""
    echo "🌐 Actualiza la configuración en tu frontend web:"
    echo "   API_BASE_URL = '$SERVICE_URL';"
else
    print_warning "El servicio está desplegado pero puede tener problemas (HTTP $HTTP_STATUS)"
    echo "Verifica los logs con: gcloud run services logs tail $SERVICE_NAME --region $REGION"
fi

print_success "🚀 Despliegue completado!"
