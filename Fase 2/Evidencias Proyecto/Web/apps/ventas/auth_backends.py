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
            # Try to find the cliente by email or RUT
            cliente = ClientePersona.objects.get(email=username)
            
            # For now, we'll use a simple password verification
            # You might want to implement proper password hashing later
            if self.verify_password(password, cliente):
                # Create or get corresponding User object
                user, created = User.objects.get_or_create(
                    username=cliente.email,
                    defaults={
                        'email': cliente.email,
                        'first_name': cliente.nombres,
                        'last_name': f"{cliente.apellido_paterno} {cliente.apellido_materno}",
                        'is_active': cliente.estado,
                    }
                )
                
                # Store cliente_persona_id in user for later reference
                user.cliente_persona_id = cliente.cliente_persona_id
                return user
                
        except ClientePersona.DoesNotExist:
            try:
                # Also try with RUT
                cliente = ClientePersona.objects.get(rut=username)
                if self.verify_password(password, cliente):
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
                pass
        
        return None
    
    def verify_password(self, password, cliente):
            """
            Simple password verification. 
            For demo purposes, we'll use email as password.
            In production, you should implement proper password hashing.
            """
            # For demo: password is the first part of email (before @)
            expected_password = cliente.password  # Assuming password is stored hashed
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return password_hash == expected_password
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None