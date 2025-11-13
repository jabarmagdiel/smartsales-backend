#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import json

def test_reports():
    User = get_user_model()
    client = Client()

    # Obtener usuario admin
    admin_user = User.objects.filter(is_staff=True).first()
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)

    print(f'✅ Usuario admin: {admin_user.username}')

    # Probar endpoint de plantillas
    print('\n🔍 Probando /api/v1/templates/')
    response = client.get(
        '/api/v1/templates/',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )

    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = json.loads(response.content)
        templates = data.get('results', data) if isinstance(data, dict) else data
        print(f'✅ Plantillas disponibles: {len(templates)}')
        for template in templates[:3]:
            print(f'  - {template["name"]} ({template["category"]})')
    else:
        print(f'❌ Error: {response.content.decode()}')

    # Probar generación de reporte predefinido
    print('\n🔍 Generando reporte de ventas...')
    response = client.post(
        '/api/v1/reports/generate_predefined/',
        data=json.dumps({'template_id': 1, 'parameters': {}}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )

    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f'✅ Reporte generado: {data["title"]}')
        if isinstance(data["data"], dict):
            print(f'✅ Datos disponibles: {list(data["data"].keys())}')
        else:
            print(f'✅ Datos: {type(data["data"])}')
    else:
        print(f'❌ Error: {response.content.decode()}')

    # Probar consulta personalizada
    print('\n🔍 Probando consulta personalizada...')
    response = client.post(
        '/api/v1/reports/generate_custom/',
        data=json.dumps({'query_text': 'productos más vendidos'}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )

    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f'✅ Reporte personalizado: {data["title"]}')
    else:
        print(f'❌ Error: {response.content.decode()}')

if __name__ == '__main__':
    test_reports()
