#!/usr/bin/env python3
import os
import sys
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings_production')

def run_command(command):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔧 Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Éxito: {command}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error en: {command}")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Excepción en {command}: {e}")
        return False

def setup_database():
    """Configurar base de datos paso a paso"""
    print("🚀 Configurando base de datos PostgreSQL...")
    
    # 1. Verificar conexión
    try:
        import django
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL conectado: {version[0]}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 2. Crear migraciones si no existen
    print("\n📝 Creando migraciones...")
    run_command("python3 manage.py makemigrations --settings=backend_salessmart.settings_production")
    
    # 3. Aplicar migraciones de Django primero
    print("\n🔧 Aplicando migraciones de Django...")
    commands = [
        "python3 manage.py migrate contenttypes --settings=backend_salessmart.settings_production",
        "python3 manage.py migrate auth --settings=backend_salessmart.settings_production", 
        "python3 manage.py migrate sessions --settings=backend_salessmart.settings_production",
        "python3 manage.py migrate admin --settings=backend_salessmart.settings_production",
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            print(f"⚠️ Falló: {cmd}, continuando...")
    
    # 4. Aplicar todas las migraciones
    print("\n🔧 Aplicando todas las migraciones...")
    run_command("python3 manage.py migrate --settings=backend_salessmart.settings_production")
    
    # 5. Crear superusuario si no existe
    print("\n👤 Verificando superusuario...")
    try:
        from users.models import User
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@smartsales.com',
                password='admin123',
                first_name='Admin',
                last_name='SmartSales'
            )
            print("✅ Superusuario creado: admin/admin123")
        else:
            print("✅ Superusuario ya existe")
    except Exception as e:
        print(f"⚠️ Error creando superusuario: {e}")
    
    print("✅ Configuración de base de datos completada")
    return True

if __name__ == '__main__':
    setup_database()
