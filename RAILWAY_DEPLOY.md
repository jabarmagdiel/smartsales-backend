# 🚀 Despliegue en Railway - SmartSales Backend

## 📋 Pasos para Desplegar

### 1. Preparar el Proyecto
```bash
# Asegúrate de que todos los archivos estén actualizados
git add .
git commit -m "Preparar para despliegue en Railway"
git push origin main
```

### 2. Configurar Variables de Entorno en Railway

En el panel de Railway, configura estas variables:

```env
SECRET_KEY=tu-clave-secreta-muy-segura-de-50-caracteres-minimo
DEBUG=False
DJANGO_SETTINGS_MODULE=backend_salessmart.settings_railway
RAILWAY_ENVIRONMENT=production
```

### 3. Base de Datos PostgreSQL

Railway creará automáticamente la variable `DATABASE_URL`. No necesitas configurarla manualmente.

### 4. Comandos de Despliegue

Railway ejecutará automáticamente:
1. `pip install -r requirements.txt`
2. `python manage.py migrate --settings=backend_salessmart.settings_railway`
3. `python manage.py collectstatic --noinput --settings=backend_salessmart.settings_railway`
4. `gunicorn backend_salessmart.wsgi:application --bind 0.0.0.0:$PORT`

## 🔧 Librerías de Reportes

Las siguientes librerías están incluidas para la generación de reportes:

- **WeasyPrint**: Para generar PDFs avanzados
- **OpenPyXL**: Para generar archivos Excel
- **ReportLab**: Para PDFs alternativos
- **CairoCFfi**: Dependencia para WeasyPrint

## 🐛 Solución de Problemas

### Error: "weasyprint not found"
Si ves este error, verifica que las dependencias del sistema estén instaladas:
- Cairo
- Pango
- GDK-Pixbuf
- libffi

El archivo `nixpacks.toml` incluye estas dependencias.

### Error: "No module named 'openpyxl'"
Verifica que `requirements.txt` incluya:
```
openpyxl==3.1.2
```

### Error de Base de Datos
1. Verifica que la base de datos PostgreSQL esté creada en Railway
2. Asegúrate de que `DATABASE_URL` esté configurada automáticamente
3. Revisa los logs para errores de migración

### Error de Archivos Estáticos
Los archivos estáticos se manejan con WhiteNoise. Si hay problemas:
1. Verifica que `STATIC_ROOT` esté configurado
2. Ejecuta `collectstatic` manualmente en los logs

## 📊 Verificar Despliegue

Una vez desplegado, verifica:

1. **API Base**: `https://tu-app.railway.app/api/v1/`
2. **Admin**: `https://tu-app.railway.app/admin/`
3. **Swagger**: `https://tu-app.railway.app/swagger/`
4. **Reportes**: `https://tu-app.railway.app/api/v1/reports/`

## 🔍 Logs y Debugging

Para ver los logs en Railway:
```bash
railway logs
```

Los prints de configuración aparecerán como:
```
🚀 Configuración Railway cargada
🔧 DEBUG: False
✅ WeasyPrint disponible para PDFs
✅ OpenPyXL disponible para Excel
✅ ReportLab disponible para PDFs
```

## 🌐 CORS y Frontend

El backend está configurado para aceptar requests de cualquier origen en desarrollo. Para producción, actualiza `CORS_ALLOWED_ORIGINS` en `settings_railway.py`.

## 📱 Próximos Pasos

1. Configurar el frontend para usar la URL de Railway
2. Configurar variables de entorno del frontend
3. Probar la funcionalidad de reportes PDF/Excel
4. Configurar dominio personalizado (opcional)
