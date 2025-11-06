from rest_framework import serializers
from .models import Return, Warranty

class ReturnSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Return
        fields = ('id', 'order', 'order_id', 'product', 'product_name', 'quantity', 'reason', 'status', 'created_at', 'processed_by')
        read_only_fields = ('id', 'created_at', 'processed_by')

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
