from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

    def get_total(self, obj):
        return obj.total

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'subtotal')
        read_only_fields = ('id',)

    def get_subtotal(self, obj):
        return obj.subtotal

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'total', 'shipping_cost', 'address', 'items', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    shipping_method = serializers.CharField()

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'amount', 'method', 'status', 'transaction_id', 'created_at')
        read_only_fields = ('id', 'created_at')
