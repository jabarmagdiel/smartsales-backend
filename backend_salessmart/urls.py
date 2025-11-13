# backend_salessmart/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)
from users.serializers import MyTokenObtainPairSerializer

# Swagger / OpenAPI
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="SmartSales API",
        default_version='v1',
        description="Documentación de la API SmartSales",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

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
    # Logística disponible con y sin prefijo 'logistics/'
    path('api/v1/', include('logistics.urls')),
    path('api/v1/logistics/', include('logistics.urls')),
    # Posventa (Garantías y Devoluciones)
    path('api/v1/', include('posventa.urls')),
    # Sistema de Reportes Inteligente (CU15-CU20)
    path('api/v1/', include('reports.urls')),
    path('api/v1/', include('logs.urls')),
    path('api/v1/reportes/', include('reportes.urls')),
    path('api/v1/ia/', include('ia.urls')),
    # System backups
    path('api/v1/system/backups/', views.list_backups, name='list_backups'),
    path('api/v1/system/backups/create/', views.create_backup, name='create_backup'),
    path('api/v1/system/backups/<str:filename>/download/', views.download_backup, name='download_backup'),
    path('api/v1/system/backups/restore/', views.restore_backup, name='restore_backup'),

    # Swagger/OpenAPI endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)