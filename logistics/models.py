from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product

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
