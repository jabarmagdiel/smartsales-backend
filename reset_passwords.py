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

def reset_passwords():
    print("=== RESETEO DE CONTRASEÑAS ===")
    
    # Resetear contraseña del admin
    try:
        admin = User.objects.get(username='renechungara')
        admin.set_password('admin123')
        admin.save()
        print("OK Contraseña de 'renechungara' reseteada a: admin123")
    except User.DoesNotExist:
        print("X Usuario 'renechungara' no encontrado")
    
    # Resetear contraseña del admin2
    try:
        admin2 = User.objects.get(username='admin2')
        admin2.set_password('admin123')
        admin2.save()
        print("OK Contraseña de 'admin2' reseteada a: admin123")
    except User.DoesNotExist:
        print("X Usuario 'admin2' no encontrado")
    
    # Resetear contraseña del operador
    try:
        operador = User.objects.get(username='operador@gmail.com')
        operador.set_password('operador123')
        operador.save()
        print("OK Contraseña de 'operador@gmail.com' reseteada a: operador123")
    except User.DoesNotExist:
        print("X Usuario 'operador@gmail.com' no encontrado")
    
    # Resetear contraseña del cliente
    try:
        cliente = User.objects.get(username='cliente_demo')
        cliente.set_password('cliente123')
        cliente.save()
        print("OK Contraseña de 'cliente_demo' reseteada a: cliente123")
    except User.DoesNotExist:
        print("X Usuario 'cliente_demo' no encontrado")
    
    # Resetear contraseña del admin básico
    try:
        admin_basic = User.objects.get(username='admin')
        admin_basic.set_password('admin123')
        admin_basic.save()
        print("OK Contraseña de 'admin' reseteada a: admin123")
    except User.DoesNotExist:
        print("X Usuario 'admin' no encontrado")
    
    print("\n=== CREDENCIALES ACTUALIZADAS ===")
    print("Administradores:")
    print("   Usuario: renechungara | Contraseña: admin123")
    print("   Usuario: admin2       | Contraseña: admin123")
    print("   Usuario: admin        | Contraseña: admin123")
    print("\nOperador:")
    print("   Usuario: operador@gmail.com | Contraseña: operador123")
    print("\nCliente:")
    print("   Usuario: cliente_demo | Contraseña: cliente123")

if __name__ == '__main__':
    reset_passwords()
