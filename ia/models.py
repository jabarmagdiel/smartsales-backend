from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product

class ModeloConfiguracion(models.Model):
    n_estimators = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    date_range_start = models.DateField()
    date_range_end = models.DateField()

    def __str__(self):
        return f"Config: {self.n_estimators} estimators, {self.date_range_start} to {self.date_range_end}"

class HistoricalSale(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} - {self.date} - {self.quantity}"

class TrainingSession(models.Model):
    last_training_datetime = models.DateTimeField(auto_now=True)
    rmse = models.FloatField()
    mae = models.FloatField()
    r2 = models.FloatField()

    def __str__(self):
        return f"Training {self.last_training_datetime}: RMSE={self.rmse}, MAE={self.mae}, R2={self.r2}"
