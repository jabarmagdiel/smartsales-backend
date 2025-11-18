#!/usr/bin/env python3
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings_production')

try:
    import django
    django.setup()
    
    from django.db import connection
    from django.core.management import execute_from_command_line
    
    print("🔍 Verificando estado de la base de datos PostgreSQL...")
    
    # Verificar conexión
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conexión PostgreSQL: {version[0]}")
        
        # Verificar tablas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📊 Tablas existentes ({len(tables)}):")
        
        django_tables = []
        user_tables = []
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('django_') or table_name.startswith('auth_'):
                django_tables.append(table_name)
            else:
                user_tables.append(table_name)
            print(f"  - {table_name}")
        
        print(f"\n📋 Resumen:")
        print(f"  - Tablas de Django: {len(django_tables)}")
        print(f"  - Tablas de usuario: {len(user_tables)}")
        
        # Verificar si existen las tablas críticas de Django
        critical_tables = ['django_migrations', 'auth_user', 'django_session']
        missing_tables = []
        
        for critical in critical_tables:
            if critical not in [t[0] for t in tables]:
                missing_tables.append(critical)
        
        if missing_tables:
            print(f"❌ Tablas críticas faltantes: {missing_tables}")
            print("🔧 Se necesitan migraciones")
        else:
            print("✅ Tablas críticas de Django presentes")
            
            # Verificar usuarios si existe la tabla
            if 'auth_user' in [t[0] for t in tables]:
                cursor.execute("SELECT COUNT(*) FROM auth_user;")
                user_count = cursor.fetchone()[0]
                print(f"👥 Usuarios en auth_user: {user_count}")
                
            # Verificar tabla personalizada de usuarios
            if 'users_user' in [t[0] for t in tables]:
                cursor.execute("SELECT COUNT(*) FROM users_user;")
                custom_user_count = cursor.fetchone()[0]
                print(f"👥 Usuarios en users_user: {custom_user_count}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("✅ Verificación completada")
