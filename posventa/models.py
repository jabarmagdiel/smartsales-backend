from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product
from users.models import User
from sales.models import Order

class Return(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
        ('PROCESSED', 'Procesado'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_returns')

    def __str__(self):
        return f"Return for Order {self.order.id} - {self.product.name}"

class Warranty(models.Model):
    RESOLUTION_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('RESOLVED', 'Resuelto'),
        ('REJECTED', 'Rechazado'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warranties')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='warranties')
    duration_months = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    resolution_status = models.CharField(max_length=10, choices=RESOLUTION_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Warranty for {self.product.name}"

    @property
    def vigente(self):
        from django.utils import timezone
        return self.is_active and timezone.now() <= self.end_date
