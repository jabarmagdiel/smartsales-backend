#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.test import Client
import json

User = get_user_model()

def test_endpoints():
    # Obtener usuario de prueba
    try:
        user = User.objects.get(username='test_cliente')
        print(f'✅ Usuario encontrado: {user.username}')
        
        # Generar token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Crear cliente de prueba
        client = Client()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        
        print('\n🔍 Probando nuevos endpoints...')
        
        # 1. Probar endpoint de órdenes disponibles
        print('\n1. Probando /devoluciones/available_orders/')
        response = client.get('/api/v1/devoluciones/available_orders/', **headers)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f'   ✅ Órdenes disponibles: {len(data)}')
            for order in data:
                print(f'      - Orden {order["id"]}: {len(order["items"])} items')
        else:
            print(f'   ❌ Error: {response.content.decode()}')
        
        # 2. Probar endpoint de devoluciones del usuario
        print('\n2. Probando /devoluciones/')
        response = client.get('/api/v1/devoluciones/', **headers)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if isinstance(data, dict) and 'results' in data:
                print(f'   ✅ Devoluciones del usuario: {len(data["results"])}')
            elif isinstance(data, list):
                print(f'   ✅ Devoluciones del usuario: {len(data)}')
        else:
            print(f'   ❌ Error: {response.content.decode()}')
            
        # 3. Probar endpoint de gestión (como admin)
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            print(f'\n3. Probando como admin: {admin_user.username}')
            admin_refresh = RefreshToken.for_user(admin_user)
            admin_token = str(admin_refresh.access_token)
            admin_headers = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
            
            response = client.get('/api/v1/gestion-devoluciones/', **admin_headers)
            print(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                data = json.loads(response.content)
                if isinstance(data, dict) and 'results' in data:
                    print(f'   ✅ Todas las devoluciones: {len(data["results"])}')
                elif isinstance(data, list):
                    print(f'   ✅ Todas las devoluciones: {len(data)}')
            else:
                print(f'   ❌ Error: {response.content.decode()}')
        
        print('\n✅ Pruebas completadas')
        
    except User.DoesNotExist:
        print('❌ Usuario test_cliente no encontrado')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    test_endpoints()
