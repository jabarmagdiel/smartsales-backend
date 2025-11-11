from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserProfileSerializer, LoginSerializer, UserManagementSerializer
from .permissions import IsAdminUser, IsOperator

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
class UserViewSet(viewsets.ModelViewSet):
    """
    Endpoint para Administradores para gestionar todos los usuarios (CU4).
    """
    queryset = User.objects.all().order_by('username')
    # Usa el serializer que muestra más campos (sin la contraseña)
    serializer_class = UserManagementSerializer 
    # Solo los Admins pueden ver y gestionar la lista de usuarios
    permission_classes = [IsAuthenticated, IsAdminUser]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserManagementSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsOperator]

    def get_queryset(self):
        # Los operadores pueden gestionar usuarios, pero no superusuarios
        if self.request.user.role == 'OPERATOR':
            return User.objects.exclude(is_superuser=True)
        return User.objects.all()

    def perform_update(self, serializer):
        # Los operadores no pueden cambiar el rol de otros operadores o admins
        if self.request.user.role == 'OPERATOR':
            instance = self.get_object()
            if instance.role in ['OPERATOR', 'ADMIN'] or instance.is_superuser:
                raise PermissionError("No tienes permisos para modificar este usuario.")
        serializer.save()

    def perform_destroy(self, instance):
        # Los operadores no pueden eliminar superusuarios
        if self.request.user.role == 'OPERATOR' and instance.is_superuser:
            raise PermissionError("No tienes permisos para eliminar este usuario.")
        instance.delete()
