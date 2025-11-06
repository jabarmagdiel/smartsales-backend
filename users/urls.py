from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ProfileView, LogoutView, UserManagementViewSet

router = DefaultRouter()
router.register(r'usuarios', UserManagementViewSet)

urlpatterns = [
    path('registro/', RegisterView.as_view(), name='register'),
    path('token/', LoginView.as_view(), name='token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', ProfileView.as_view(), name='profile'),
] + router.urls
