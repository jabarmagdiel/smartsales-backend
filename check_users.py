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

def check_users():
    print("=== USUARIOS EN LA BASE DE DATOS ===")
    users = User.objects.all()
    
    if not users.exists():
        print("X No hay usuarios en la base de datos")
        print("\n=== CREANDO USUARIO ADMINISTRADOR ===")
        
        # Crear usuario admin por defecto
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@smartsales.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        print("OK Usuario administrador creado:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")
        print(f"   Rol: ADMIN")
        
        # Crear usuario operador
        operator_user = User.objects.create_user(
            username='operador',
            email='operador@smartsales.com',
            password='operador123',
            first_name='Operador',
            last_name='Sistema'
        )
        operator_user.role = 'OPERATOR'
        operator_user.is_staff = True
        operator_user.is_superuser = False
        operator_user.save()
        
        print("OK Usuario operador creado:")
        print(f"   Usuario: operador")
        print(f"   Contraseña: operador123")
        print(f"   Rol: OPERATOR")
        
        # Crear usuario cliente
        client_user = User.objects.create_user(
            username='cliente',
            email='cliente@smartsales.com',
            password='cliente123',
            first_name='Cliente',
            last_name='Prueba'
        )
        client_user.role = 'CLIENT'
        client_user.is_staff = False
        client_user.is_superuser = False
        client_user.save()
        
        print("OK Usuario cliente creado:")
        print(f"   Usuario: cliente")
        print(f"   Contraseña: cliente123")
        print(f"   Rol: CLIENT")
        
    else:
        print(f"OK Se encontraron {users.count()} usuarios:")
        for user in users:
            print(f"   - {user.username} ({user.role}) - Activo: {user.is_active}")
    
    print("\n=== CREDENCIALES SUGERIDAS ===")
    print("Para administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\nPara operador:")
    print("   Usuario: operador") 
    print("   Contraseña: operador123")
    print("\nPara cliente:")
    print("   Usuario: cliente")
    print("   Contraseña: cliente123")

if __name__ == '__main__':
    check_users()
