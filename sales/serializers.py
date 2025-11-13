from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, Return
from products.models import Product

class ProductCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'sku', 'image', 'price')


class CartItemSerializer(serializers.ModelSerializer):
    # Lectura: objeto producto compacto
    product = ProductCompactSerializer(read_only=True)
    # Escritura: product_id para añadir/actualizar (si se usa el serializer para escribir)
    product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True, required=False)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'price', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

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
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'payment_method', 'payment_method_display', 'total', 'shipping_cost', 'address', 'items', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    shipping_method = serializers.CharField()

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class ReturnSerializer(serializers.ModelSerializer):
    """Serializer para devoluciones"""
    
    # Campos de solo lectura para mostrar información relacionada
    order_number = serializers.CharField(source='order.id', read_only=True)
    product_name = serializers.CharField(source='order_item.product.name', read_only=True)
    product_sku = serializers.CharField(source='order_item.product.sku', read_only=True)
    product_price = serializers.DecimalField(source='order_item.price', max_digits=10, decimal_places=2, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    # Campos calculados
    can_be_returned = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    
    class Meta:
        model = Return
        fields = [
            'id', 'order', 'order_item', 'user',
            'reason', 'reason_display', 'description', 'quantity',
            'status', 'status_display', 'requested_at', 'processed_at', 'completed_at',
            'refund_amount', 'admin_notes', 'attachment',
            # Campos relacionados
            'order_number', 'product_name', 'product_sku', 'product_price',
            'user_name', 'user_email', 'can_be_returned'
        ]
        read_only_fields = ['id', 'requested_at', 'processed_at', 'completed_at', 'refund_amount']
    
    def validate_quantity(self, value):
        """Validar que la cantidad no exceda la cantidad original del pedido"""
        if self.instance:
            # En caso de actualización
            order_item = self.instance.order_item
        else:
            # En caso de creación
            order_item = self.initial_data.get('order_item')
            if order_item:
                from .models import OrderItem
                order_item = OrderItem.objects.get(id=order_item)
        
        if order_item and value > order_item.quantity:
            raise serializers.ValidationError(
                f"No puedes devolver más de {order_item.quantity} unidades."
            )
        
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        order_item = data.get('order_item')
        
        if order_item:
            # Verificar que el producto pueda ser devuelto (dentro de 30 días)
            from datetime import timedelta
            from django.utils import timezone
            
            if (timezone.now() - order_item.order.created_at) > timedelta(days=30):
                raise serializers.ValidationError(
                    "No se pueden solicitar devoluciones después de 30 días de la compra."
                )
            
            # Verificar que no haya una devolución pendiente para este item
            existing_return = Return.objects.filter(
                order_item=order_item,
                status__in=['REQUESTED', 'APPROVED', 'PROCESSING']
            ).first()
            
            if existing_return:
                raise serializers.ValidationError(
                    f"Ya existe una devolución {existing_return.get_status_display().lower()} para este producto."
                )
        
        return data


class ReturnCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear devoluciones"""
    
    class Meta:
        model = Return
        fields = ['order_item', 'reason', 'description', 'quantity', 'attachment']
    
    def create(self, validated_data):
        """Crear devolución asignando automáticamente el usuario y la orden"""
        order_item = validated_data['order_item']
        validated_data['user'] = self.context['request'].user
        validated_data['order'] = order_item.order
        
        return super().create(validated_data)
