# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'password')
        read_only_fields = ('id', 'role',) # 'role' es read_only porque lo manejamos en 'create'

    def create(self, validated_data):
        # (Esta lógica de 'create' ya es correcta)
        role = validated_data.pop('role', 'CLIENT') # Default a CLIENT (valor interno)
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        phone = validated_data.pop('phone', None)
        address = validated_data.pop('address', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        
        user.role = role
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.address = address
        user.save()
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address')
        read_only_fields = ('id', 'username', 'role')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include username and password.')

        return data


# --- INICIO DE LA CORRECCIÓN (Error de Rol "CLIENT") ---
class UserManagementSerializer(serializers.ModelSerializer):
    # 1. Define 'role' como un campo calculado
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    # 2. Implementa la función que calcula el rol
    def get_role(self, obj):
        # Esta lógica asegura que los superusuarios SIEMPRE se muestren como 'Administrador'
        if obj.is_superuser:
            return 'Administrador'
        if obj.is_staff:
            return 'Operador'
        # Si no es staff, usa el rol de la DB (ej: 'CLIENTE' o 'Cliente')
        return obj.role 
# --- FIN DE LA CORRECCIÓN ---


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        if user.is_superuser:
            token['role'] = 'Administrador'
        elif user.is_staff:
            token['role'] = 'Operador'
        else:
            token['role'] = 'Cliente'
            
        token['username'] = user.username
        return token