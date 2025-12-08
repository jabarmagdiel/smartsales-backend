"""
Script para generar órdenes de prueba con datos realistas
Uso: python manage.py generate_orders 1000
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from users.models import User
from products.models import Product
from sales.models import Order, OrderItem


class Command(BaseCommand):
    help = 'Genera órdenes de prueba con datos realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            'cantidad',
            type=int,
            default=100,
            help='Número de órdenes a generar'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        # Obtener usuarios y productos
        usuarios = list(User.objects.filter(role='cliente'))
        productos = list(Product.objects.filter(stock__gt=0))
        
        if not usuarios:
            self.stdout.write(self.style.ERROR('No hay usuarios clientes en la BD'))
            return
        
        if not productos:
            self.stdout.write(self.style.ERROR('No hay productos en la BD'))
            return
        
        self.stdout.write(f'Generando {cantidad} órdenes...')
        
        ordenes_creadas = 0
        
        for i in range(cantidad):
            try:
                # Usuario aleatorio
                usuario = random.choice(usuarios)
                
                # Fecha aleatoria en los últimos 6 meses
                dias_atras = random.randint(0, 180)
                fecha_orden = timezone.now() - timedelta(days=dias_atras)
                
                # Estado aleatorio con probabilidades realistas
                estados = [
                    ('PENDING', 5),
                    ('CONFIRMED', 10),
                    ('PAID', 15),
                    ('SHIPPED', 25),
                    ('DELIVERED', 40),
                    ('CANCELLED', 5),
                ]
                estado = random.choices(
                    [e[0] for e in estados],
                    weights=[e[1] for e in estados]
                )[0]
                
                # Método de pago
                metodos_pago = ['CASH', 'PAYPAL', 'STRIPE']
                metodo_pago = random.choice(metodos_pago)
                
                # Dirección de envío
                direcciones = [
                    'Av. Principal 123, Ciudad, País',
                    'Calle Secundaria 456, Urbanización, País',
                    'Carrera 7 #89-12, Barrio Centro, País',
                    'Transversal 45 #23-67, Sector Norte, País',
                ]
                direccion = random.choice(direcciones)
                
                # Crear orden
                orden = Order.objects.create(
                    user=usuario,
                    status=estado,
                    payment_method=metodo_pago,
                    total=Decimal('0.00'),  # Se calculará después
                    shipping_cost=Decimal('0.00'),
                    address=direccion,
                    created_at=fecha_orden,
                    updated_at=fecha_orden,
                )
                
                # Agregar items (de 1 a 5 productos por orden)
                num_items = random.randint(1, 5)
                total_orden = Decimal('0.00')
                
                productos_orden = random.sample(productos, min(num_items, len(productos)))
                
                for producto in productos_orden:
                    cantidad_item = random.randint(1, 3)
                    precio = producto.price
                    
                    OrderItem.objects.create(
                        order=orden,
                        product=producto,
                        quantity=cantidad_item,
                        price=precio,
                    )
                    
                    total_orden += precio * cantidad_item
                
                # Actualizar total de la orden
                orden.total = total_orden
                orden.save()
                
                ordenes_creadas += 1
                
                if (i + 1) % 100 == 0:
                    self.stdout.write(f'  Creadas {i + 1}/{cantidad} órdenes...')
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error al crear orden {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ {ordenes_creadas} órdenes creadas exitosamente!'
            )
        )
