# logistics/serializers.py
from rest_framework import serializers
from .models import InventoryMovement, Alert, Recommendation
from products.models import Product 

# --- SERIALIZADOR PARA LEER PRODUCTOS (USADO EN INVENTARIO) ---
class ProductForInventorySerializer(serializers.ModelSerializer):
    """Serializer simple para mostrar solo el nombre/sku del producto en el historial"""
    class Meta:
        model = Product
        # --- CORRECCIÓN ---
        # El modelo de Product usa 'name' (según tu código anterior).
        fields = ['id', 'name', 'sku'] 
        # --- FIN DE CORRECCIÓN ---

class InventoryMovementSerializer(serializers.ModelSerializer):
    # 'producto' será un objeto anidado (read-only)
    producto = ProductForInventorySerializer(read_only=True)
    
    # 'producto_id' será usado para escribir (write-only)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = InventoryMovement
        fields = [
            'id', 
            'producto', 
            'producto_id',
            'tipo_movimiento', 
            'cantidad', 
            'motivo', 
            'fecha_movimiento'
        ]
        read_only_fields = ('fecha_movimiento',)

# --- Serializadores existentes (Alertas y Recomendaciones) ---
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'