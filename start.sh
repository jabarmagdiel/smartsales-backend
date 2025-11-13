#!/bin/bash

# Script de inicio para Railway
echo "🚀 Iniciando SmartSales Backend en Railway..."

# Ejecutar migraciones
echo "📦 Ejecutando migraciones..."
python manage.py migrate --settings=backend_salessmart.settings_railway

# Recoger archivos estáticos
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --settings=backend_salessmart.settings_railway

# Crear superusuario si no existe (opcional)
echo "👤 Verificando superusuario..."
python manage.py shell --settings=backend_salessmart.settings_railway << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@smartsales.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
EOF

# Iniciar servidor
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn backend_salessmart.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile -
