from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product
from users.models import User

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmado'),
        ('PAID', 'Pagado'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Efectivo (Pago contra entrega)'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Tarjeta de crédito'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    
    def create_warranties(self):
        """Crear garantías de 1 año para todos los productos de la orden"""
        from posventa.models import Warranty
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        for item in self.items.all():
            # Crear garantía de 1 año para cada producto
            start_date = timezone.now()
            end_date = start_date + timedelta(days=365)  # 1 año
            
            Warranty.objects.get_or_create(
                product=item.product,
                order=self,
                defaults={
                    'duration_months': 12,
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': True,
                    'resolution_status': 'PENDING'
                }
            )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='PAYPAL')
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.order.id} - {self.status}"

class Return(models.Model):
    """Modelo para gestionar devoluciones de productos"""
    
    STATUS_CHOICES = [
        ('REQUESTED', 'Solicitada'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
        ('PROCESSING', 'En Proceso'),
        ('COMPLETED', 'Completada'),
    ]
    
    REASON_CHOICES = [
        ('DEFECTIVE', 'Producto Defectuoso'),
        ('WRONG_ITEM', 'Producto Incorrecto'),
        ('NOT_AS_DESCRIBED', 'No Como se Describió'),
        ('DAMAGED_SHIPPING', 'Dañado en Envío'),
        ('CHANGED_MIND', 'Cambio de Opinión'),
        ('SIZE_ISSUE', 'Problema de Talla/Tamaño'),
        ('OTHER', 'Otro'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='product_returns')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='returns')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_returns')
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(help_text="Descripción detallada del motivo de devolución")
    quantity = models.PositiveIntegerField(default=1, help_text="Cantidad a devolver")
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='REQUESTED')
    
    # Fechas
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Notas del administrador")
    
    # Archivos adjuntos (opcional)
    attachment = models.FileField(upload_to='returns/', null=True, blank=True, help_text="Foto del producto dañado, etc.")
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
    
    def __str__(self):
        return f"Devolución #{self.id} - {self.order_item.product.name} - {self.get_status_display()}"
    
    @property
    def can_be_returned(self):
        """Verifica si el producto puede ser devuelto (dentro de 30 días)"""
        from datetime import timedelta
        from django.utils import timezone
        
        return (timezone.now() - self.order.created_at) <= timedelta(days=30)
    
    def approve(self, admin_user, refund_amount=None):
        """Aprobar la devolución"""
        self.status = 'APPROVED'
        self.processed_at = timezone.now()
        if refund_amount:
            self.refund_amount = refund_amount
        else:
            self.refund_amount = self.order_item.price * self.quantity
        self.save()
        
        # Log de la acción
        from logs.models import LogEntry
        LogEntry.objects.create(
            user=admin_user,
            action=f"Devolución #{self.id} aprobada - Producto: {self.order_item.product.name} - Monto: ${self.refund_amount}",
            ip_address='SYSTEM'
        )
    
    def reject(self, admin_user, reason=""):
        """Rechazar la devolución"""
        self.status = 'REJECTED'
        self.processed_at = timezone.now()
        if reason:
            self.admin_notes = reason
        self.save()
        
        # Log de la acción
        from logs.models import LogEntry
        LogEntry.objects.create(
            user=admin_user,
            action=f"Devolución #{self.id} rechazada - Producto: {self.order_item.product.name} - Razón: {reason}",
            ip_address='SYSTEM'
        )
