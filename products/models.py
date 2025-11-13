from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    warranty_months = models.PositiveIntegerField(default=12, validators=[MinValueValidator(0)], help_text="Tiempo de garantía en meses")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.price}"

class AtributoProducto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='atributos')
    nombre = models.CharField(max_length=100)  # e.g., 'Tamaño de Pantalla', 'Material'
    valor = models.CharField(max_length=200)  # e.g., '15.6 pulgadas', 'Aluminio'

    def __str__(self):
        return f"{self.product.name} - {self.nombre}: {self.valor}"

class InventoryMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"
