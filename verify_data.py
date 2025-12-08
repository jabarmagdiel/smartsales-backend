import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from sales.models import Order, OrderItem, OrderTracking
from users.models import User

print('=' * 50)
print('📊 RESUMEN DE DATOS GENERADOS')
print('=' * 50)
print(f'👥 Usuarios clientes: {User.objects.filter(role="cliente").count()}')
print(f'📦 Órdenes totales: {Order.objects.count()}')
print(f'📋 Items de órdenes: {OrderItem.objects.count()}')
print(f'🔍 Registros de tracking: {OrderTracking.objects.count()}')
print()
print('Estados de órdenes:')
from django.db.models import Count
for status in Order.objects.values('status').annotate(count=Count('id')).order_by('-count'):
    print(f'  - {status["status"]}: {status["count"]}')
print('=' * 50)
