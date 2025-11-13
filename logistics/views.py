import os
from datetime import datetime, timedelta

# Importaciones condicionales para machine learning
try:
    import joblib
    import pandas as pd
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False
    joblib = None
    pd = None
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from products.models import Product
from ia.models import HistoricalSale
from .models import Alert, Recommendation, InventoryMovement # 1. Importa InventoryMovement
from .serializers import (
    AlertSerializer, 
    RecommendationSerializer, 
    InventoryMovementSerializer # 2. Importa el nuevo serializer
)
from users.permissions import IsAdminUser, IsOperator



MODEL_PATH = 'ia_model.pkl'

class InventoryMovementViewSet(viewsets.ModelViewSet):
    """
    Endpoint para ver y crear movimientos de inventario (CU3).
    """
    queryset = InventoryMovement.objects.all().order_by('-fecha_movimiento')
    serializer_class = InventoryMovementSerializer
    # Usamos el nombre corregido 'IsOperator'
    permission_classes = [IsAuthenticated, (IsAdminUser | IsOperator)]  
      
class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Alert.objects.all().order_by('-created_at')

    @action(detail=False, methods=['post'])
    def generate_alerts(self, request):
        """Generate alerts based on stock levels and IA predictions"""
        alerts_created = 0

        # Load IA model if available
        model = None
        if HAS_ML_LIBS and os.path.exists(MODEL_PATH):
            try:
                model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Error loading ML model: {e}")
                model = None

        products = Product.objects.all()
        for product in products:
            # Check low stock
            if product.stock <= product.min_stock:
                Alert.objects.get_or_create(
                    product=product,
                    alert_type='LOW_STOCK',
                    resolved=False,
                    defaults={
                        'message': f'Stock level ({product.stock}) is below minimum ({product.min_stock})',
                        'threshold': product.min_stock,
                        'current_stock': product.stock,
                    }
                )
                alerts_created += 1

            # Check overstock (if stock > 2x min_stock and no recent sales)
            if product.stock > product.min_stock * 2:
                recent_sales = HistoricalSale.objects.filter(
                    product=product,
                    date__gte=datetime.now().date() - timedelta(days=30)
                ).count()
                if recent_sales == 0:
                    Alert.objects.get_or_create(
                        product=product,
                        alert_type='OVERSTOCK',
                        resolved=False,
                        defaults={
                            'message': f'Overstock detected: {product.stock} units with no sales in 30 days',
                            'threshold': product.min_stock * 2,
                            'current_stock': product.stock,
                        }
                    )
                    alerts_created += 1

            # Check prediction discrepancy if model available
            if model and HAS_ML_LIBS and pd:
                try:
                    # Predict next week's demand
                    next_week = datetime.now().date() + timedelta(days=7)
                    features = {
                        'month': [next_week.month],
                        'day_of_week': [next_week.weekday()],
                        'product_id': [product.id],
                        'category_id': [product.category.id]
                    }
                    predicted = model.predict(pd.DataFrame(features))[0]
                    discrepancy = abs(product.stock - predicted)
                except Exception as e:
                    print(f"Error making prediction: {e}")
                    continue

                if discrepancy > product.min_stock:
                    Alert.objects.get_or_create(
                        product=product,
                        alert_type='PREDICTION_DISCREPANCY',
                        resolved=False,
                        defaults={
                            'message': f'Stock ({product.stock}) vs Predicted demand ({predicted:.1f}) discrepancy',
                            'threshold': int(discrepancy),
                            'current_stock': product.stock,
                            'predicted_demand': predicted,
                        }
                    )
                    alerts_created += 1

        return Response({'alerts_created': alerts_created})

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.resolved = True
        alert.resolved_at = datetime.now()
        alert.save()
        return Response({'status': 'resolved'})

class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Recommendation.objects.all().order_by('-created_at')

    @action(detail=False, methods=['post'])
    def generate_recommendations(self, request):
        """Generate stock recommendations using IA predictions"""
        if not HAS_ML_LIBS:
            return Response({
                'error': 'Machine learning libraries not available',
                'message': 'joblib and pandas are required for recommendations'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        recommendations_created = 0

        # Load IA model
        if not os.path.exists(MODEL_PATH):
            return Response({'error': 'IA model not available'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model = joblib.load(MODEL_PATH)
        except Exception as e:
            return Response({'error': f'Error loading model: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        products = Product.objects.all()

        for product in products:
            try:
                # Predict demand for next 30 days
                predictions = []
                for i in range(30):
                    future_date = datetime.now().date() + timedelta(days=i)
                    features = {
                        'month': [future_date.month],
                        'day_of_week': [future_date.weekday()],
                        'product_id': [product.id],
                        'category_id': [product.category.id]
                    }
                    pred = model.predict(pd.DataFrame(features))[0]
                    predictions.append(pred)
            except Exception as e:
                print(f"Error predicting for product {product.id}: {e}")
                continue

            avg_predicted_demand = sum(predictions) / len(predictions)
            recommended_stock = int(avg_predicted_demand * 1.2)  # 20% buffer

            # Create recommendation if stock is significantly different
            if abs(product.stock - recommended_stock) > product.min_stock:
                priority = 'HIGH' if abs(product.stock - recommended_stock) > product.min_stock * 2 else 'MEDIUM'

                Recommendation.objects.create(
                    product=product,
                    recommended_stock=recommended_stock,
                    reason=f'IA prediction suggests {recommended_stock} units for optimal stock level',
                    priority=priority
                )
                recommendations_created += 1

        return Response({'recommendations_created': recommendations_created})

    @action(detail=True, methods=['post'])
    def implement(self, request, pk=None):
        recommendation = self.get_object()
        # Update product stock (in real implementation, this would trigger inventory management)
        recommendation.product.stock = recommendation.recommended_stock
        recommendation.product.save()
        recommendation.implemented = True
        recommendation.save()
        return Response({'status': 'implemented'})
