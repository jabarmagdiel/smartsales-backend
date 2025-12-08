# SmartSales Backend - Django REST API

Backend completo para sistema de ventas con Django REST Framework.

## 🚀 Deploy Rápido en Railway

### Paso 1: Crear proyecto en Railway
1. Ve a [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Selecciona este repositorio

### Paso 2: Agregar PostgreSQL
- Click "New" → "Database" → "PostgreSQL"

### Paso 3: Variables de Entorno
Agrega en Settings → Variables:
```
SECRET_KEY=tu-secret-key-aqui
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### Paso 4: Deploy
- Railway detectará automáticamente la configuración
- Espera a que termine el deploy (2-3 minutos)
- ¡Listo! Tu API estará en `https://tu-proyecto.railway.app`

### Crear Admin:
```bash
railway run python create_superuser.py
```

## 📚 Documentación Completa
Ver `railway_deploy_guide.md` en los artifacts para la guía completa paso a paso.

## 🔗 Endpoints Principales
- API Docs: `/swagger/`
- Admin: `/admin/`
- Productos: `/api/v1/productos/productos/`
- Reviews: `/api/v1/productos/reviews/`
- Órdenes: `/api/v1/ventas/orders/`

## 🛠️ Desarrollo Local
```bash
python manage.py runserver
```

## ✨ Funcionalidades
- ✅ Sistema de reseñas con calificaciones
- ✅ Rastreo de pedidos en tiempo real
- ✅ Búsqueda avanzada con filtros
- ✅ Autenticación JWT
- ✅ WebSockets para notificaciones
- ✅ Machine Learning para recomendaciones
