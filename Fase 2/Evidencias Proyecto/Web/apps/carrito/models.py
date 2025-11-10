from django.db import models

# Modelo para almacenar información temporal del checkout
class CheckoutSession(models.Model):
    """
    Almacena temporalmente la información del checkout mientras se procesa el pago
    """
    session_id = models.CharField(max_length=255, unique=True)
    
    # Información del cliente
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    rut = models.CharField(max_length=12)
    
    # Información de envío
    calle = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    # Información del pedido
    total = models.IntegerField()
    subtotal = models.IntegerField()
    costo_envio = models.IntegerField(default=2990)
    
    # Información de Transbank
    transbank_token = models.CharField(max_length=255, blank=True, null=True)
    transbank_url = models.URLField(blank=True, null=True)
    
    # Estado del checkout
    estado = models.CharField(max_length=50, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('error', 'Error'),
    ])
    
    # IDs de cliente (si están autenticados)
    cliente_persona_id = models.IntegerField(blank=True, null=True)
    cliente_empresa_id = models.IntegerField(blank=True, null=True)
    
    # Datos del carrito en formato JSON
    carrito_data = models.JSONField()
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'checkout_session'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Checkout {self.session_id} - {self.estado}"

