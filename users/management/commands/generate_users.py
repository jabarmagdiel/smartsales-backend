"""
Script para generar usuarios de prueba
"""
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Genera usuarios de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            'cantidad',
            type=int,
            default=50,
            help='Número de usuarios a generar'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        self.stdout.write(f'Generando {cantidad} usuarios clientes...')
        
        usuarios_creados = 0
        
        for i in range(cantidad):
            try:
                email = f'cliente{i+1}@test.com'
                
                # Verificar si ya existe
                if User.objects.filter(email=email).exists():
                    continue
                
                User.objects.create_user(
                    username=f'cliente{i+1}',
                    email=email,
                    password='password123',
                    first_name=f'Cliente{i+1}',
                    last_name='Test',
                    phone=f'+1234567{i:04d}',
                    role='cliente',
                    is_active=True,
                )
                usuarios_creados += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error al crear usuario {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ {usuarios_creados} usuarios creados exitosamente!'
            )
        )
