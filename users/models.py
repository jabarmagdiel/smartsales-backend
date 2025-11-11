from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio")

        email = self.normalize_email(email)
        # Extraer role de extra_fields si está presente, default 'CLIENT'
        role = extra_fields.pop('role', 'CLIENT')
        user = self.model(username=username, email=email, role=role, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'ADMIN')   # Asigna ADMIN automáticamente

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('CLIENT', 'Cliente'),
        ('OPERATOR', 'Operador'),
        ('ADMIN', 'Administrador'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    objects = UserManager()

    def __str__(self):
        return self.username
