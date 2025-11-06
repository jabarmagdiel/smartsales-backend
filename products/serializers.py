from rest_framework import serializers
from .models import Category, Product, Price, InventoryMovement, AtributoProducto

class AtributoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtributoProducto
        fields = ('id', 'nombre', 'valor')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all())
    atributos = AtributoProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'
        read_only_fields = ('created_at',)

class InventoryMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    stock_actual = serializers.SerializerMethodField()

    class Meta:
        model = InventoryMovement
        fields = '__all__'
        read_only_fields = ('created_at',)

    def get_stock_actual(self, obj):
        return obj.product.stock
