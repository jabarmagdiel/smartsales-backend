# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Asumimos que estas vistas (LoginView, etc.) las tienes definidas
    LoginView, 
    ProfileView, 
    LogoutView, 
    UserManagementViewSet, 
    UserCreateView, # Esta es la vista que crea el usuario
    UserViewSet
)

router = DefaultRouter()

# Nombres base (basename) únicos para los ViewSets
router.register(r'usuarios', UserManagementViewSet, basename='user-management')
router.register(r'users', UserViewSet, basename='user-detail') # Para el GET de Clientes (Admin)

urlpatterns = [
    # --- CORRECCIÓN DEL 404 ---
    # Apunta la URL 'register/' (la que llama el frontend) a la vista 'UserCreateView'
    path('register/', UserCreateView.as_view(), name='user-register'),
    # --- FIN DE LA CORRECCIÓN ---
    
    # Mantenemos las rutas de autenticación que tenías (si las usas)
    path('token/', LoginView.as_view(), name='token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', ProfileView.as_view(), name='profile'),
    
    # Incluimos las rutas del router (usuarios y users)
] + router.urls