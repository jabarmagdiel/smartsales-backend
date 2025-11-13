#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_token_for_user(username):
    try:
        user = User.objects.get(username=username)
        
        # Generar token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        print(f'✅ Tokens generados para {username}:')
        print(f'Access Token: {access_token[:50]}...')
        print(f'Refresh Token: {refresh_token[:50]}...')
        print()
        print('📋 Para usar en el navegador (copia y pega en Console):')
        print(f'localStorage.setItem("access_token", "{access_token}");')
        print(f'localStorage.setItem("refresh_token", "{refresh_token}");')
        print('console.log("✅ Tokens guardados");')
        
        return access_token, refresh_token
        
    except User.DoesNotExist:
        print(f'❌ Usuario {username} no encontrado')
        return None, None

if __name__ == '__main__':
    # Generar token para test_cliente
    generate_token_for_user('test_cliente')
