"""
Script rápido para crear superusuario en Railway
Ejecutar con: railway run python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings_railway')
django.setup()

from users.models import User

# Configuración del superusuario
ADMIN_EMAIL = 'admin@smartsales.com'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'AdminPass123!'  # CAMBIAR ESTO en producción

if not User.objects.filter(email=ADMIN_EMAIL).exists():
    user = User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        first_name='Admin',
        last_name='SmartSales',
        role='admin',
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    print(f'✓ Superusuario creado exitosamente!')
    print(f'  Email: {ADMIN_EMAIL}')
    print(f'  Username: {ADMIN_USERNAME}')
    print(f'  Password: {ADMIN_PASSWORD}')
    print(f'\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login!')
else:
    print(f'⚠️  Usuario {ADMIN_EMAIL} ya existe')
    print('Si olvidaste la contraseña, usa: railway run python manage.py changepassword admin')
