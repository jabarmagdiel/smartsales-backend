from rest_framework import serializers
from .models import Category, Product, Price, InventoryMovement, AtributoProducto, Review

class AtributoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtributoProducto
        fields = ('id', 'nombre', 'valor')

class CategorySerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='name')

    class Meta:
        model = Category
        fields = ('id', 'nombre', 'description')

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer para reseñas de productos"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'product', 'user_id', 'user_name', 'username', 'rating', 'title', 
                 'comment', 'is_verified_purchase', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user_id', 'user_name', 'username', 'is_verified_purchase', 
                           'created_at', 'updated_at')
    
    def create(self, validated_data):
        # Agregar el usuario autenticado
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    categoria = CategorySerializer(source='category', read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    nombre = serializers.CharField(source='name')
    precio = serializers.CharField(source='price')
    stock_actual = serializers.IntegerField(source='stock')
    meses_garantia = serializers.IntegerField(source='warranty_months')
    atributos = AtributoProductoSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    # Campos para ratings
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    current_price = serializers.FloatField(read_only=True)
    # Compatibilidad de solo lectura para clientes que esperan 'name' y 'stock'
    name = serializers.CharField(read_only=True)
    stock = serializers.IntegerField(read_only=True)
    warranty_months = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'nombre', 'name', 'categoria', 'categoria_id', 'precio', 'stock', 'stock_actual', 
                 'min_stock', 'meses_garantia', 'warranty_months', 'atributos', 'sku', 'description', 
                 'image', 'average_rating', 'review_count', 'current_price', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'average_rating', 'review_count', 'current_price')

class ProductDetailSerializer(ProductSerializer):
    """Serializer extendido con reseñas para vista de detalle"""
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ('reviews',)

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
