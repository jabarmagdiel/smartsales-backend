#!/usr/bin/env python
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from sales.models import OrderItem

User = get_user_model()

def test_return_api():
    try:
        # Obtener usuario de prueba
        user = User.objects.get(username='test_cliente')
        print(f'✅ Usuario: {user.username}')
        
        # Generar token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Obtener un OrderItem para probar
        order_item = OrderItem.objects.filter(order__user=user, order__status='DELIVERED').first()
        if not order_item:
            print('❌ No hay OrderItems DELIVERED para el usuario')
            return
            
        print(f'✅ OrderItem: {order_item.id} - {order_item.product.name}')
        
        # Datos para la devolución
        data = {
            'order_item': order_item.id,
            'reason': 'DEFECTIVE',
            'description': 'Producto no funciona correctamente - Prueba API',
            'quantity': 1
        }
        
        # Headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print('\n🔍 Probando POST /api/v1/devoluciones/')
        print(f'Datos: {data}')
        
        # Hacer petición POST
        response = requests.post(
            'http://localhost:8000/api/v1/devoluciones/',
            json=data,
            headers=headers
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 201:
            result = response.json()
            print(f'✅ Devolución creada exitosamente:')
            print(f'   ID: {result.get("id")}')
            print(f'   Mensaje: {result.get("message")}')
            print(f'   Producto: {result.get("product_name")}')
        else:
            print(f'❌ Error: {response.status_code}')
            try:
                error_data = response.json()
                print(f'   Detalles: {error_data}')
            except:
                print(f'   Respuesta: {response.text}')
        
        # Verificar que aparezca en gestión
        print('\n🔍 Verificando en gestión de devoluciones...')
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            admin_refresh = RefreshToken.for_user(admin_user)
            admin_token = str(admin_refresh.access_token)
            admin_headers = {
                'Authorization': f'Bearer {admin_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'http://localhost:8000/api/v1/gestion-devoluciones/',
                headers=admin_headers
            )
            
            if response.status_code == 200:
                returns = response.json()
                if isinstance(returns, dict) and 'results' in returns:
                    returns = returns['results']
                print(f'✅ Total devoluciones en gestión: {len(returns)}')
                for ret in returns[-3:]:  # Mostrar las últimas 3
                    print(f'   - ID: {ret["id"]} | {ret.get("product_name", "N/A")} | {ret.get("status", "N/A")}')
            else:
                print(f'❌ Error al obtener gestión: {response.status_code}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    test_return_api()
