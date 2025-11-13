from rest_framework import serializers
from .models import Return, Warranty

class ReturnSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    order_item = serializers.IntegerField(write_only=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='order.user.username', read_only=True)
    processed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Return
        fields = ('id', 'order', 'order_id', 'order_number', 'product', 'product_name', 'product_sku', 'quantity', 'reason', 'status', 'status_display', 'created_at', 'processed_by', 'processed_by_name', 'order_item', 'user_name')
        read_only_fields = ('id', 'created_at', 'processed_by')
        extra_kwargs = {
            'order': {'required': False},
            'product': {'required': False},
        }
    
    def get_processed_by_name(self, obj):
        if obj.processed_by:
            return f"{obj.processed_by.first_name} {obj.processed_by.last_name}".strip() or obj.processed_by.username
        return None
    
    def validate(self, data):
        # Validar que se proporcione order_item O (order y product)
        order_item = data.get('order_item')
        order = data.get('order')
        product = data.get('product')
        
        if not order_item and (not order or not product):
            raise serializers.ValidationError(
                'Debe proporcionar order_item o ambos order y product'
            )
        
        return data
    
    def create(self, validated_data):
        # Si se proporciona order_item, extraer order y product
        order_item_id = validated_data.pop('order_item', None)
        if order_item_id:
            from sales.models import OrderItem
            try:
                order_item = OrderItem.objects.get(id=order_item_id)
                validated_data['order'] = order_item.order
                validated_data['product'] = order_item.product
            except OrderItem.DoesNotExist:
                raise serializers.ValidationError({'order_item': 'OrderItem no encontrado'})
        
        return super().create(validated_data)

class WarrantySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    vigente = serializers.SerializerMethodField()

    class Meta:
        model = Warranty
        fields = ('id', 'product', 'product_name', 'order', 'order_id', 'duration_months', 'start_date', 'end_date', 'is_active', 'resolution_status', 'vigente')
        read_only_fields = ('id',)

    def get_vigente(self, obj):
        return obj.vigente
