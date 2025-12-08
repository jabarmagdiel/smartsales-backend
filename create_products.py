#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from products.models import Product, Category
from decimal import Decimal

def create_sample_products():
    print("🛒 Creando productos de prueba...")
    
    # Crear categoría
    cat, created = Category.objects.get_or_create(
        name='Electrónicos', 
        defaults={'description': 'Productos electrónicos'}
    )
    print(f'📁 Categoría: {cat.name} ({"creada" if created else "existente"})')
    
    # Crear productos
    productos = [
        {'name': 'iPhone 15', 'sku': 'IPH15-001', 'price': Decimal('999.99'), 'stock': 10},
        {'name': 'Samsung Galaxy S24', 'sku': 'SGS24-001', 'price': Decimal('899.99'), 'stock': 15},
        {'name': 'MacBook Pro', 'sku': 'MBP-001', 'price': Decimal('1999.99'), 'stock': 5},
        {'name': 'iPad Air', 'sku': 'IPA-001', 'price': Decimal('599.99'), 'stock': 8},
        {'name': 'AirPods Pro', 'sku': 'APP-001', 'price': Decimal('249.99'), 'stock': 20},
    ]
    
    for prod_data in productos:
        prod, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'description': f'Descripción de {prod_data["name"]}',
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'category': cat,
            }
        )
        print(f'📱 Producto: {prod.name} - ${prod.price} ({"creado" if created else "existente"})')
    
    print(f'\n✅ Total productos en BD: {Product.objects.count()}')
    print(f'✅ Productos con stock: {Product.objects.filter(stock__gt=0).count()}')

if __name__ == '__main__':
    create_sample_products()
