"""
Script para importar órdenes desde CSV
Formato esperado del CSV:
user_email,product_sku,quantity,price,status,payment_method,address,date
"""
from django.core.management.base import BaseCommand
import csv
from datetime import datetime

from users.models import User
from products.models import Product
from sales.models import Order, OrderItem


class Command(BaseCommand):
    help = 'Importa órdenes desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Ruta al archivo CSV'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            ordenes_creadas = 0
            orden_actual = None
            
            for row in reader:
                try:
                    # Obtener o crear usuario
                    user = User.objects.get(email=row['user_email'])
                    
                    # Verificar si necesitamos crear nueva orden
                    # (agrupa items por user+date+address)
                    fecha = datetime.strptime(row['date'], '%Y-%m-%d')
                    
                    if (orden_actual is None or 
                        orden_actual.user != user or 
                        orden_actual.created_at.date() != fecha.date()):
                        
                        # Crear nueva orden
                        orden_actual = Order.objects.create(
                            user=user,
                            status=row.get('status', 'PENDING'),
                            payment_method=row.get('payment_method', 'CASH'),
                            total=0,
                            address=row['address'],
                            created_at=fecha,
                        )
                        ordenes_creadas += 1
                    
                    # Agregar item a la orden
                    producto = Product.objects.get(sku=row['product_sku'])
                    OrderItem.objects.create(
                        order=orden_actual,
                        product=producto,
                        quantity=int(row['quantity']),
                        price=float(row['price']),
                    )
                    
                    # Actualizar total
                    orden_actual.total += float(row['price']) * int(row['quantity'])
                    orden_actual.save()
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error en línea: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {ordenes_creadas} órdenes importadas!'
                )
            )
