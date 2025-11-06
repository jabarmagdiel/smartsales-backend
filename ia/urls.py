from django.urls import path
from . import views

urlpatterns = [
    path('data/generate/', views.GenerateDataView.as_view(), name='generate_data'),
    path('train/', views.TrainView.as_view(), name='train'),
    path('predict/', views.PredictView.as_view(), name='predict'),
    path('status/', views.StatusView.as_view(), name='status'),
]
