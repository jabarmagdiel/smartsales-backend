"""
URL configuration for backend_salessmart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.root_view, name='root'),
    path('admin/', admin.site.urls),
    path('admin/backup/', views.backup_database, name='backup_database'),
    path('api/v1/', include('products.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('sales.urls')),
    path('api/v1/', include('logistics.urls')),
    path('api/v1/', include('posventa.urls')),
    path('api/v1/', include('logs.urls')),
    path('api/v1/reportes/', include('reportes.urls')),
    path('api/v1/ia/', include('ia.urls')),
]
