from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product

class InventoryMovement(models.Model):
    """
    Registra cada entrada o salida de stock para un producto (CU3).
    """
    TIPO_MOVIMIENTO_CHOICES = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    )

    producto = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='movimientos'
    )
    tipo_movimiento = models.CharField(
        max_length=10, 
        choices=TIPO_MOVIMIENTO_CHOICES
    )
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        default='Ajuste manual'
    )
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} para {self.producto.name}"
    
    # --- (Lógica para actualizar el stock real del producto) ---
    # (Esto es avanzado, pero profesional. Cuando se guarda un movimiento,
    # actualiza el stock en el modelo 'Product')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Guarda el movimiento primero
        
        # Actualiza el stock en el producto relacionado
        if self.tipo_movimiento == 'ENTRADA':
            self.producto.stock += self.cantidad
        elif self.tipo_movimiento == 'SALIDA':
            # Evita stock negativo
            if self.producto.stock >= self.cantidad:
                self.producto.stock -= self.cantidad
            else:
                # (En un sistema real, lanzarías un error aquí)
                self.producto.stock = 0
        
        self.producto.save(update_fields=['stock'])



class Alert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock Alert'),
        ('OVERSTOCK', 'Overstock Alert'),
        ('PREDICTION_DISCREPANCY', 'Prediction vs Stock Discrepancy'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=25, choices=ALERT_TYPES)
    message = models.TextField()
    threshold = models.PositiveIntegerField(default=0)
    current_stock = models.PositiveIntegerField(default=0)
    predicted_demand = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.alert_type} - {self.product.name}"

class Recommendation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommendations')
    recommended_stock = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.TextField()
    priority = models.CharField(max_length=10, choices=[
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ], default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    implemented = models.BooleanField(default=False)

    def __str__(self):
        return f"Recommendation for {self.product.name} - {self.recommended_stock} units"
