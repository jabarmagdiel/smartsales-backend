#!/usr/bin/env python
"""
Script para corregir los métodos de pago de órdenes existentes
basándose en los registros de Payment
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_salessmart.settings')
django.setup()

from sales.models import Order, Payment

def fix_payment_methods():
    """
    Corregir métodos de pago basándose en los registros de Payment existentes
    """
    print("Iniciando correccion de metodos de pago...")
    
    # Obtener todas las órdenes
    orders = Order.objects.all()
    updated_count = 0
    
    for order in orders:
        # Buscar el pago asociado a esta orden
        payment = Payment.objects.filter(order=order).first()
        
        if payment:
            # Si existe un pago, usar su método
            old_method = order.payment_method
            order.payment_method = payment.method
            order.save()
            
            if old_method != payment.method:
                print(f"OK Orden #{order.id}: {old_method} -> {payment.method}")
                updated_count += 1
            else:
                print(f"INFO Orden #{order.id}: Ya tenia {payment.method} (correcto)")
        else:
            # Si no hay pago, mantener como CASH (probablemente sea correcto)
            print(f"WARN Orden #{order.id}: Sin pago registrado, mantiene CASH")
    
    print(f"\nCorreccion completada!")
    print(f"Ordenes actualizadas: {updated_count}")
    print(f"Total de ordenes: {orders.count()}")

def show_payment_summary():
    """
    Mostrar resumen de métodos de pago después de la corrección
    """
    print("\nRESUMEN DE METODOS DE PAGO:")
    
    from django.db.models import Count
    
    summary = Order.objects.values('payment_method').annotate(
        count=Count('id')
    ).order_by('payment_method')
    
    for item in summary:
        method = item['payment_method']
        count = item['count']
        
        if method == 'CASH':
            name = 'Efectivo (Contra entrega)'
        elif method == 'PAYPAL':
            name = 'PayPal'
        elif method == 'STRIPE':
            name = 'Tarjeta de credito'
        else:
            name = method
            
        print(f"{name}: {count} ordenes")

if __name__ == '__main__':
    try:
        fix_payment_methods()
        show_payment_summary()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
