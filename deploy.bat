@echo off
REM 🚀 Script de despliegue para Windows - SmartSales Backend en Google Cloud

echo.
echo ========================================
echo   SMARTSALES BACKEND - GOOGLE CLOUD
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "manage.py" (
    echo [ERROR] Este script debe ejecutarse desde el directorio del backend
    echo         donde se encuentra manage.py
    pause
    exit /b 1
)

REM Obtener PROJECT_ID
for /f "tokens=*" %%i in ('gcloud config get-value project 2^>nul') do set PROJECT_ID=%%i
if "%PROJECT_ID%"=="" (
    echo [ERROR] No se pudo obtener el PROJECT_ID
    echo         Ejecuta: gcloud config set project YOUR_PROJECT_ID
    pause
    exit /b 1
)

echo [INFO] Desplegando en proyecto: %PROJECT_ID%
echo.

REM Verificar dependencias
echo [INFO] Verificando dependencias...
gcloud version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Google Cloud SDK no está instalado
    pause
    exit /b 1
)

docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está instalado
    pause
    exit /b 1
)

echo [SUCCESS] Dependencias verificadas
echo.

REM Habilitar APIs
echo [INFO] Habilitando APIs necesarias...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
echo [SUCCESS] APIs habilitadas
echo.

REM Crear secretos
echo [INFO] Configurando secretos...
gcloud secrets describe django-secret-key >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creando Django secret key...
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" | gcloud secrets create django-secret-key --data-file=-
    echo [SUCCESS] Django secret key creado
) else (
    echo [WARNING] Django secret key ya existe
)
echo.

REM Usar requirements de producción
echo [INFO] Preparando requirements de producción...
copy requirements-production.txt requirements.txt >nul
echo [SUCCESS] Requirements actualizados
echo.

REM Construir imagen
echo [INFO] Construyendo imagen Docker...
set IMAGE_NAME=gcr.io/%PROJECT_ID%/smartsales-backend
gcloud builds submit --tag %IMAGE_NAME%
if errorlevel 1 (
    echo [ERROR] Error al construir la imagen
    pause
    exit /b 1
)
echo [SUCCESS] Imagen construida: %IMAGE_NAME%
echo.

REM Desplegar en Cloud Run
echo [INFO] Desplegando en Cloud Run...
set SERVICE_NAME=smartsales-backend
set REGION=us-central1

gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --set-env-vars GOOGLE_CLOUD_PROJECT=%PROJECT_ID% ^
    --set-env-vars DJANGO_SETTINGS_MODULE=backend_salessmart.settings_production ^
    --memory 1Gi ^
    --cpu 1 ^
    --max-instances 10 ^
    --min-instances 0 ^
    --port 8080 ^
    --timeout 300

if errorlevel 1 (
    echo [ERROR] Error al desplegar en Cloud Run
    pause
    exit /b 1
)

echo [SUCCESS] Servicio desplegado en Cloud Run
echo.

REM Obtener URL del servicio
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo [SUCCESS] Servicio disponible en: %SERVICE_URL%
echo.

REM Verificar despliegue
echo [INFO] Verificando despliegue...
curl -s -o nul -w "%%{http_code}" "%SERVICE_URL%/api/v1/productos/" > temp_status.txt
set /p HTTP_STATUS=<temp_status.txt
del temp_status.txt

if "%HTTP_STATUS%"=="200" (
    echo [SUCCESS] ✅ Despliegue exitoso!
) else if "%HTTP_STATUS%"=="401" (
    echo [SUCCESS] ✅ Despliegue exitoso! (Requiere autenticación)
) else (
    echo [WARNING] El servicio puede tener problemas (HTTP %HTTP_STATUS%)
    echo             Verifica los logs con: gcloud run services logs tail %SERVICE_NAME% --region %REGION%
)

echo.
echo ========================================
echo           DESPLIEGUE COMPLETADO
echo ========================================
echo.
echo 🌐 URL del servicio: %SERVICE_URL%
echo 🔧 Panel de admin: %SERVICE_URL%/admin/
echo 📊 API: %SERVICE_URL%/api/v1/
echo.
echo 📱 Actualiza tu app móvil:
echo    lib/core/config/api_config.dart
echo    baseUrl = '%SERVICE_URL%';
echo.
echo 🌐 Actualiza tu frontend web:
echo    API_BASE_URL = '%SERVICE_URL%';
echo.
echo 🚀 ¡Despliegue completado exitosamente!
echo.
pause
