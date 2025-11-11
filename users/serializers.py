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
        read_only_fields = ('id',)  # Removed 'role' to make it editable

    def create(self, validated_data):
        role = validated_data.pop('role', 'CLIENT')  # Default to CLIENT
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

        # Set is_staff and is_superuser based on role
        if role == 'ADMIN':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'OPERATOR':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False

        user.save()
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', instance.role)
        instance.role = role

        # Set is_staff and is_superuser based on role
        if role == 'ADMIN':
            instance.is_superuser = True
            instance.is_staff = True
        elif role == 'OPERATOR':
            instance.is_staff = True
            instance.is_superuser = False
        else:
            instance.is_staff = False
            instance.is_superuser = False

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

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


class UserManagementSerializer(serializers.ModelSerializer):
    role = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        role = validated_data.pop('role', 'CLIENT')
        user = super().create(validated_data)
        user.role = role

        # Set is_staff and is_superuser based on role
        if role == 'ADMIN':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'OPERATOR':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False

        user.save()
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', instance.role)
        instance.role = role

        # Set is_staff and is_superuser based on role
        if role == 'ADMIN':
            instance.is_superuser = True
            instance.is_staff = True
        elif role == 'OPERATOR':
            instance.is_staff = True
            instance.is_superuser = False
        else:
            instance.is_staff = False
            instance.is_superuser = False

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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