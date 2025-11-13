#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from users.models import User

def create_admin():
    print("=== CREANDO USUARIO ADMINISTRADOR ===")
    
    # Eliminar usuario admin existente si existe
    try:
        existing_admin = User.objects.get(username='admin')
        existing_admin.delete()
        print("Usuario 'admin' existente eliminado")
    except User.DoesNotExist:
        pass
    
    # Crear nuevo usuario administrador
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@smartsales.com',
        password='admin123',
        first_name='Administrador',
        last_name='SmartSales'
    )
    
    # Configurar como administrador
    admin_user.role = 'ADMIN'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.save()
    
    print("OK Usuario administrador creado exitosamente!")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("   Rol: ADMIN")
    print("   Email: admin@smartsales.com")
    
    # Crear usuario operador
    try:
        existing_operator = User.objects.get(username='operador')
        existing_operator.delete()
        print("Usuario 'operador' existente eliminado")
    except User.DoesNotExist:
        pass
    
    operator_user = User.objects.create_user(
        username='operador',
        email='operador@smartsales.com',
        password='operador123',
        first_name='Operador',
        last_name='SmartSales'
    )
    
    operator_user.role = 'OPERATOR'
    operator_user.is_staff = True
    operator_user.is_superuser = False
    operator_user.is_active = True
    operator_user.save()
    
    print("OK Usuario operador creado exitosamente!")
    print("   Usuario: operador")
    print("   Contraseña: operador123")
    print("   Rol: OPERATOR")
    
    # Crear usuario cliente
    try:
        existing_client = User.objects.get(username='cliente')
        existing_client.delete()
        print("Usuario 'cliente' existente eliminado")
    except User.DoesNotExist:
        pass
    
    client_user = User.objects.create_user(
        username='cliente',
        email='cliente@smartsales.com',
        password='cliente123',
        first_name='Cliente',
        last_name='Demo'
    )
    
    client_user.role = 'CLIENT'
    client_user.is_staff = False
    client_user.is_superuser = False
    client_user.is_active = True
    client_user.save()
    
    print("OK Usuario cliente creado exitosamente!")
    print("   Usuario: cliente")
    print("   Contraseña: cliente123")
    print("   Rol: CLIENT")
    
    print("\n=== CREDENCIALES PARA LOGIN ===")
    print("ADMINISTRADOR:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\nOPERADOR:")
    print("   Usuario: operador")
    print("   Contraseña: operador123")
    print("\nCLIENTE:")
    print("   Usuario: cliente")
    print("   Contraseña: cliente123")

if __name__ == '__main__':
    create_admin()
