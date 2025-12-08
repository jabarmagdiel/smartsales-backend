from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
    @property
    def average_rating(self):
        """Calcula el rating promedio del producto"""
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('rating'))
        return round(result['rating__avg'], 1) if result['rating__avg'] else 0.0
    
    @property
    def review_count(self):
        """Retorna el número total de reseñas"""
        return self.reviews.count()
    
    @property
    def current_price(self):
        """Retorna el precio actual del producto"""
        return float(self.price)

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

class Review(models.Model):
    """
    Modelo para reseñas y calificaciones de productos
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False, help_text="¿El usuario compró este producto?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Un usuario solo puede dejar una reseña por producto
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"
    
    def save(self, *args, **kwargs):
        # Verificar si es una compra verificada
        from sales.models import Order, OrderItem
        if not self.is_verified_purchase:
            # Verificar si el usuario ha comprado este producto
            has_purchased = OrderItem.objects.filter(
                order__user=self.user,
                product=self.product,
                order__status__in=['PAID', 'SHIPPED', 'DELIVERED']
            ).exists()
            self.is_verified_purchase = has_purchased
        super().save(*args, **kwargs)

