"""
Comando para crear usuarios administradores del dashboard
Uso: python manage.py create_dashboard_admin
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
import getpass


class Command(BaseCommand):
    help = 'Crear un usuario administrador para el dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario para el administrador',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email del administrador',
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='Nombre del administrador',
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Apellido del administrador',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña del administrador',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Creador de Usuario Administrador del Dashboard ===')
        )
        
        # Obtener username
        username = options.get('username')
        if not username:
            username = input('Nombre de usuario: ').strip()
        
        if not username:
            raise CommandError('El nombre de usuario es obligatorio')
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            raise CommandError(f'El usuario "{username}" ya existe')
        
        # Obtener email
        email = options.get('email')
        if not email:
            email = input('Email (opcional): ').strip()
        
        # Obtener nombres
        first_name = options.get('first_name')
        if not first_name:
            first_name = input('Nombre (opcional): ').strip()
        
        last_name = options.get('last_name')
        if not last_name:
            last_name = input('Apellido (opcional): ').strip()
        
        # Obtener contraseña
        password = options.get('password')
        if not password:
            password = getpass.getpass('Contraseña: ')
            if len(password) < 8:
                raise CommandError('La contraseña debe tener al menos 8 caracteres')
            
            password_confirm = getpass.getpass('Confirmar contraseña: ')
            if password != password_confirm:
                raise CommandError('Las contraseñas no coinciden')
        
        try:
            with transaction.atomic():
                # Crear el usuario
                user = User.objects.create_user(
                    username=username,
                    email=email or '',
                    password=password,
                    first_name=first_name or '',
                    last_name=last_name or ''
                )
                
                # Otorgar permisos de staff y superusuario
                user.is_staff = True
                user.is_superuser = True
                user.save()
                
            self.stdout.write()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuario administrador "{username}" creado exitosamente!')
            )
            self.stdout.write(f'   - Username: {username}')
            self.stdout.write(f'   - Email: {email or "No especificado"}')
            full_name = f'{first_name} {last_name}'.strip()
            self.stdout.write(f'   - Nombre completo: {full_name or "No especificado"}')
            self.stdout.write(f'   - Permisos: Staff y Superusuario')
            self.stdout.write()
            self.stdout.write(
                self.style.SUCCESS('Ya puedes usar este usuario para acceder al dashboard en /dashboard/login/')
            )
            
        except Exception as e:
            raise CommandE