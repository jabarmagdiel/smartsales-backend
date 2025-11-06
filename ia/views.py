import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import joblib
import os
from .models import HistoricalSale, ModeloConfiguracion, TrainingSession
from products.models import Product

MODEL_PATH = 'ia_model.pkl'

@method_decorator(csrf_exempt, name='dispatch')
class GenerateDataView(APIView):
    def post(self, request):
        # Generate synthetic data
        products = list(Product.objects.all())
        if not products:
            return Response({"error": "No products available"}, status=status.HTTP_400_BAD_REQUEST)

        start_date = datetime.now() - timedelta(days=365*2)  # 2 years ago
        end_date = datetime.now()
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        data = []
        for date in dates:
            for product in products:
                # Random quantity between 1 and 50
                quantity = np.random.randint(1, 51)
                data.append(HistoricalSale(date=date.date(), product=product, quantity=quantity))

        # Bulk create
        HistoricalSale.objects.bulk_create(data)

        return Response({"message": f"Generated {len(data)} synthetic sales records"}, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class TrainView(APIView):
    def post(self, request):
        # Load data
        sales = HistoricalSale.objects.all().values('date', 'product__id', 'product__category__id', 'quantity')
        df = pd.DataFrame(list(sales))
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['product_id'] = df['product__id']
        df['category_id'] = df['product__category__id']

        # Features and target
        features = ['month', 'day_of_week', 'product_id', 'category_id']
        X = df[features]
        y = df['quantity']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Get config
        config = ModeloConfiguracion.objects.first()
        if not config:
            config = ModeloConfiguracion.objects.create(n_estimators=100, date_range_start=datetime.now().date() - timedelta(days=365), date_range_end=datetime.now().date())

        # Train model
        model = RandomForestRegressor(n_estimators=config.n_estimators, random_state=42)
        model.fit(X_train, y_train)

        # Predict and metrics
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Save model
        joblib.dump(model, MODEL_PATH)

        # Save session
        TrainingSession.objects.create(rmse=rmse, mae=mae, r2=r2)

        return Response({"message": "Model trained successfully", "rmse": rmse, "mae": mae, "r2": r2}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class PredictView(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date required"}, status=status.HTTP_400_BAD_REQUEST)

        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        # Load model
        if not os.path.exists(MODEL_PATH):
            return Response({"error": "Model not trained yet"}, status=status.HTTP_400_BAD_REQUEST)
        model = joblib.load(MODEL_PATH)

        # Prepare prediction data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        products = list(Product.objects.all())
        predictions = []

        for date in dates:
            for product in products:
                features = pd.DataFrame({
                    'month': [date.month],
                    'day_of_week': [date.dayofweek],
                    'product_id': [product.id],
                    'category_id': [product.category.id]
                })
                pred = model.predict(features)[0]
                predictions.append({
                    'date': date.date().isoformat(),
                    'product_id': product.id,
                    'product_name': product.name,
                    'predicted_quantity': round(pred, 2)
                })

        # Feature importances
        feature_importances = dict(zip(['month', 'day_of_week', 'product_id', 'category_id'], model.feature_importances_))

        return Response({
            "predictions": predictions,
            "feature_importances": feature_importances
        }, status=status.HTTP_200_OK)

class StatusView(APIView):
    def get(self, request):
        session = TrainingSession.objects.last()
        if not session:
            return Response({"error": "No training session found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "last_training_datetime": session.last_training_datetime,
            "rmse": session.rmse,
            "mae": session.mae,
            "r2": session.r2
        }, status=status.HTTP_200_OK)
