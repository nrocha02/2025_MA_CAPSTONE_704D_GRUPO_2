from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import ClientePersona
import hashlib


class ClientePersonaBackend(BaseBackend):
    """
    Custom authentication backend for ClientePersona model
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Intenta encontrar a la cliente por correo electrónico
            cliente = ClientePersona.objects.get(email=username)
            
            # usaremos una verificación de contraseña simple
            if self.verify_password(password, cliente):
                # obtiene el objeto Usuario correspondiente
                user, created = User.objects.get_or_create(
                    username=cliente.email,
                    defaults={
                        'email': cliente.email,
                        'first_name': cliente.nombres,
                        'last_name': f"{cliente.apellido_paterno} {cliente.apellido_materno}",
                        'is_active': cliente.estado,
                    }
                )
                
               
                user.cliente_persona_id = cliente.cliente_persona_id
                return user
                
        except ClientePersona.DoesNotExist:
            return None
        
        return None
    
    def verify_password(self, password, cliente):

            expected_password = cliente.password  
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return password_hash == expected_password
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None