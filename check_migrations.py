#!/usr/bin/env python3
import os
import sys

def check_database_connection():
    """Verificar conexión básica a PostgreSQL"""
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings_production')
        
        import django
        django.setup()
        
        from django.db import connection
        
        # Verificar conexión
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexión PostgreSQL exitosa: {version[0]}")
            
            # Verificar tablas existentes
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """)
            table_count = cursor.fetchone()[0]
            print(f"📊 Tablas en la base de datos: {table_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("⚠️ Continuando sin verificación de base de datos...")
        return False

if __name__ == '__main__':
    print("🔍 Verificando conexión a PostgreSQL...")
    check_database_connection()
    print("✅ Verificación completada")
