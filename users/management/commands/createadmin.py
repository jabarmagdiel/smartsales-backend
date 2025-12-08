from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Crea el usuario admin para producción"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = "admin"

        try:
            existing = User.objects.get(username=username)
            existing.delete()
            print("Usuario admin previo eliminado.")
        except User.DoesNotExist:
            pass

        user = User.objects.create_superuser(
            username="admin",
            email="admin@smartsales.com",
            password="admin123"
        )

        user.is_staff = True
        user.is_active = True
        user.save()

        print("Superusuario creado correctamente.")
