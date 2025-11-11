from rest_framework import serializers
from .models import Category, Product, Price, InventoryMovement, AtributoProducto

class AtributoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtributoProducto
        fields = ('id', 'nombre', 'valor')

class CategorySerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='name')

    class Meta:
        model = Category
        fields = ('id', 'nombre', 'description')

class ProductSerializer(serializers.ModelSerializer):
    categoria = CategorySerializer(source='category', read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    nombre = serializers.CharField(source='name')
    precio = serializers.CharField(source='price')
    stock_actual = serializers.IntegerField(source='stock')
    atributos = AtributoProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'nombre', 'categoria', 'categoria_id', 'precio', 'stock_actual', 'min_stock', 'atributos', 'sku', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'
        read_only_fields = ('created_at',)

class InventoryMovementSerializer(serializers.ModelSerializer):
    producto = serializers.SerializerMethodField()
    tipo_movimiento = serializers.CharField(source='movement_type')
    cantidad = serializers.IntegerField(source='quantity')
    motivo = serializers.CharField(source='reason')
    fecha_movimiento = serializers.DateTimeField(source='created_at')

    class Meta:
        model = InventoryMovement
        fields = ('id', 'producto', 'tipo_movimiento', 'cantidad', 'motivo', 'fecha_movimiento')
        read_only_fields = ('id', 'fecha_movimiento')

    def get_producto(self, obj):
        return {
            'id': obj.product.id,
            'nombre': obj.product.name,
            'sku': obj.product.sku
        }
