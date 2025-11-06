from rest_framework import serializers
from .models import Alert, Recommendation

class AlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'product', 'product_name', 'category_name', 'alert_type', 'message',
                 'threshold', 'current_stock', 'predicted_demand', 'created_at', 'resolved', 'resolved_at']

class RecommendationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'product', 'product_name', 'category_name', 'recommended_stock',
                 'reason', 'priority', 'created_at', 'implemented']
