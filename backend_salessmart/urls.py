# backend_salessmart/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)
from users.serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

urlpatterns = [
    path('', views.root_view, name='root'),
    path('admin/', admin.site.urls),
    path('admin/backup/', views.backup_database, name='backup_database'),
    
    path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/v1/', include('products.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('sales.urls')),
    
    # --- INICIO DE LA CORRECCIÓN (Error 404) ---
    # ANTES: path('api/v1/', include('logistics.urls')),
    # AHORA:
    path('api/v1/logistics/', include('logistics.urls')), # <-- Añadido el prefijo 'logistics/'
    # --- FIN DE LA CORRECCIÓN ---
    
    path('api/v1/', include('posventa.urls')),
    path('api/v1/', include('logs.urls')),
    path('api/v1/reportes/', include('reportes.urls')),
    path('api/v1/ia/', include('ia.urls')),
]