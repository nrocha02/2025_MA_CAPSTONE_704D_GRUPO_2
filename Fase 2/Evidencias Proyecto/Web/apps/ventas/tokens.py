"""
Generador de tokens personalizado para recuperación de contraseña de ClientePersona
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class ClienteTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, cliente, timestamp):
        """
        Hash el ID del cliente, timestamp y el estado del cliente
        """
        return (
            six.text_type(cliente.cliente_persona_id) + 
            six.text_type(timestamp) +
            six.text_type(cliente.estado)
        )


cliente_token_generator = ClienteTokenGenerator()