from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Crea un superusuario para producción"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = "admin"

        # Si existe, eliminar
        try:
            u = User.objects.get(username=username)
            u.delete()
            print("Superusuario anterior eliminado.")
        except User.DoesNotExist:
            print("No existía un admin previo.")

        # Crear nuevo superusuario
        user = User.objects.create_superuser(
            username="admin",
            email="admin@admin.com",
            password="admin123"
        )

        user.is_staff = True
        user.is_active = True
        user.save()

        print("Superusuario creado correctamente → admin / admin123")
