from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, AbstractUser


"""
Importante:
 - Se asume que las tablas y los tipos ENUM personalizados YA existen en la BD.
 - Por eso todas las clases tienen Meta.managed = False para que Django no intente crearlas/modificarlas.
 - Los tipos ENUM de PostgreSQL (estado_sesion, tipo_metodo_pago, etc.) se mapean como CharField sin choices
   para evitar inconsistencias si no conocemos todos los valores. Puedes añadir choices más adelante.
 - Las constraints complejas se replican con CheckConstraint y UniqueConstraint cuando es posible.
"""

# class User(AbstractUser):
#     email = models.EmailField('email address', unique=True)
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

class ClienteEmpresa(models.Model):
    cliente_empresa_id = models.AutoField(primary_key=True)
    rut_empresa = models.CharField(max_length=12, unique=True)
    razon_social = models.CharField(max_length=100)
    giro = models.CharField(max_length=50)
    email_contacto = models.CharField(max_length=50, unique=True)
    telefono_contacto = models.CharField(max_length=20)
    representante_legal = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'cliente_empresa'
        managed = False
        indexes = [
            models.Index(fields=['email_contacto'], name='idx_cliente_empresa_email'),
        ]

    def __str__(self):
        return f"{self.razon_social} ({self.rut_empresa})"


class ClientePersona(models.Model):
    cliente_persona_id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)
    nombres = models.CharField(max_length=25)
    apellido_paterno = models.CharField(max_length=25)
    apellido_materno = models.CharField(max_length=25)
    email = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=10)
    fecha_nacimiento = models.DateField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    password = models.CharField()
#    user = models.OneToOneField(User, on_delete=models.CASCADE)


    class Meta:
        db_table = 'cliente_persona'
        managed = False
        indexes = [
            models.Index(fields=['email'], name='idx_cliente_persona_email'),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} ({self.rut})"


class SesionInvitado(models.Model):
    cliente_invitado_id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255, unique=True)
    nombres = models.CharField(max_length=25)
    apellido_paterno = models.CharField(max_length=25)
    apellido_materno = models.CharField(max_length=25, blank=True, null=True)
    email = models.CharField(max_length=50)
    telefono = models.CharField(max_length=10)
    calle_envio = models.CharField(max_length=50)
    ciudad_envio = models.CharField(max_length=50)
    region_envio = models.CharField(max_length=50)
    codigo_postal_envio = models.SmallIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='activa')  # enum estado_sesion

    class Meta:
        db_table = 'sesion_invitado'
        managed = False

    def __str__(self):
        return f"Invitado {self.nombres} ({self.session_id})"


class UsuarioAdmin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=50, default='admin')

    class Meta:
        db_table = 'usuario_admin'
        managed = False

    def __str__(self):
        return f"{self.nombre} ({self.email})"


class Categoria(models.Model):
    categoria_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    categoria_padre = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategorias')
    nivel = models.IntegerField(default=1)
    activa = models.BooleanField(default=True)
    slug = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'categoria'
        managed = False
        constraints = [
            models.CheckConstraint(
                check=(Q(nivel=1, categoria_padre__isnull=True) | Q(nivel=2, categoria_padre__isnull=False)),
                name='chk_categoria_principal'
            ),
            models.CheckConstraint(
                check=Q(nivel__in=[1, 2]),
                name='chk_nivel_valido'
            ),
            models.UniqueConstraint(fields=['nombre', 'categoria_padre'], name='uk_nombre_categoria'),
            models.UniqueConstraint(fields=['slug'], name='categoria_slug_key'),
        ]
        indexes = [
            models.Index(fields=['activa'], name='idx_categoria_activa'),
            models.Index(fields=['nivel'], name='idx_categoria_nivel'),
            models.Index(fields=['categoria_padre'], name='idx_categoria_padre'),
            models.Index(fields=['slug'], name='idx_categoria_slug'),
        ]

    def __str__(self):
        return self.nombre


class Direccion(models.Model):
    direccion_id = models.AutoField(primary_key=True)
    cliente_persona = models.ForeignKey(ClientePersona, on_delete=models.CASCADE, blank=True, null=True)
    cliente_empresa = models.ForeignKey(ClienteEmpresa, on_delete=models.CASCADE, blank=True, null=True)
    calle = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    codigo_postal = models.SmallIntegerField()
    telefono = models.CharField(max_length=10)

    class Meta:
        db_table = 'direccion'
        managed = False
        constraints = [
            models.CheckConstraint(
                check=(
                    (Q(cliente_persona__isnull=False) & Q(cliente_empresa__isnull=True)) |
                    (Q(cliente_persona__isnull=True) & Q(cliente_empresa__isnull=False))
                ),
                name='chk_direccion_cliente_unico'
            ),
        ]

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"


class MetodoPago(models.Model):
    metodo_pago_id = models.AutoField(primary_key=True)
    cliente_persona = models.ForeignKey(ClientePersona, on_delete=models.CASCADE, blank=True, null=True)
    cliente_empresa = models.ForeignKey(ClienteEmpresa, on_delete=models.CASCADE, blank=True, null=True)
    tipo_metodo = models.CharField(max_length=50)  # enum tipo_metodo_pago
    token_seguro = models.CharField(max_length=50)
    ultimos_4_digitos = models.CharField(max_length=4)
    nombre_titular = models.CharField(max_length=50)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=50, default='activo')  # enum estado_metodo
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metodo_pago'
        managed = False
        constraints = [
            models.CheckConstraint(
                check=(
                    (Q(cliente_persona__isnull=False) & Q(cliente_empresa__isnull=True)) |
                    (Q(cliente_persona__isnull=True) & Q(cliente_empresa__isnull=False))
                ),
                name='chk_cliente_unico'
            ),
        ]

    def __str__(self):
        return f"MetodoPago {self.metodo_pago_id} ({self.tipo_metodo})"


class Marca(models.Model):
    marca_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    logo_url = models.CharField(max_length=50, blank=True, null=True)
    sitio_web = models.CharField(max_length=50, blank=True, null=True)
    slug = models.CharField(max_length=50)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'marca'
        managed = False
        constraints = [
            models.UniqueConstraint(fields=['nombre'], name='marca_nombre_key'),
            models.UniqueConstraint(fields=['slug'], name='marca_slug_key'),
        ]
        indexes = [
            models.Index(fields=['activa'], name='idx_marca_activa'),
            models.Index(fields=['slug'], name='idx_marca_slug'),
        ]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT)
    sku = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField()
    stock = models.IntegerField(default=0)
    imagen_url = models.TextField(blank=True, null=True)
    fecha_creation = models.DateTimeField(auto_now_add=True)
    estado_producto = models.CharField(max_length=50, default='activo')  # enum estado_producto
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'producto'
        managed = False
        constraints = [
            models.CheckConstraint(check=Q(precio__gte=0), name='producto_precio_check'),
            models.CheckConstraint(check=Q(stock__gte=0), name='producto_stock_check'),
        ]
        indexes = [
            models.Index(fields=['categoria'], name='idx_producto_categoria'),
            models.Index(fields=['sku'], name='idx_producto_sku'),
            models.Index(fields=['marca'], name='idx_producto_marca'),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.sku})"


class Pedido(models.Model):
    pedido_id = models.BigAutoField(primary_key=True)
    cliente_persona = models.ForeignKey(ClientePersona, on_delete=models.CASCADE, blank=True, null=True)
    cliente_empresa = models.ForeignKey(ClienteEmpresa, on_delete=models.CASCADE, blank=True, null=True)
    cliente_invitado = models.ForeignKey(SesionInvitado, on_delete=models.CASCADE, blank=True, null=True)
    calle = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    codigo_postal = models.SmallIntegerField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='Pendiente de pago')  # enum estado_pedido
    total = models.IntegerField()
    notas = models.TextField(blank=True, null=True)
    tracking_codigo = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'pedido'
        managed = False
        constraints = [
            models.CheckConstraint(
                check=(
                    (Q(cliente_persona__isnull=False) & Q(cliente_empresa__isnull=True) & Q(cliente_invitado__isnull=True)) |
                    (Q(cliente_persona__isnull=True) & Q(cliente_empresa__isnull=False) & Q(cliente_invitado__isnull=True)) |
                    (Q(cliente_persona__isnull=True) & Q(cliente_empresa__isnull=True) & Q(cliente_invitado__isnull=False))
                ),
                name='chk_pedido_cliente_unico'
            ),
            models.CheckConstraint(check=Q(total__gte=0), name='pedido_total_check'),
        ]
        indexes = [
            models.Index(fields=['cliente_empresa'], name='idx_pedido_cliente_empresa'),
            models.Index(fields=['cliente_invitado'], name='idx_pedido_cliente_invitado'),
            models.Index(fields=['cliente_persona'], name='idx_pedido_cliente_persona'),
            models.Index(fields=['estado'], name='idx_pedido_estado'),
            models.Index(fields=['fecha'], name='idx_pedido_fecha'),
        ]

    def __str__(self):
        return f"Pedido {self.pedido_id} - {self.estado}"


class PedidoRegistro(models.Model):
    registro_id = models.BigAutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    fecha_registro = models.DateField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=50)  # enum estado_pedido
    estado_actual = models.CharField(max_length=50)    # enum estado_pedido

    class Meta:
        db_table = 'pedido_registro'
        managed = False
        constraints = [
            models.CheckConstraint(check=~Q(estado_anterior=models.F('estado_actual')), name='chk_cambio_estado_pedido')
        ]

    def __str__(self):
        return f"PedidoRegistro {self.registro_id} ({self.pedido_id})"


class Sucursal(models.Model):
    sucursal_id = models.AutoField(primary_key=True)
    admin_responsable = models.ForeignKey(UsuarioAdmin, on_delete=models.RESTRICT)
    nombre = models.CharField(max_length=50, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sucursal'
        managed = False

    def __str__(self):
        return self.nombre


class Vendedor(models.Model):
    vendedor_id = models.AutoField(primary_key=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.RESTRICT)
    nombres = models.CharField(max_length=25)
    apellido_paterno = models.CharField(max_length=25)
    apellido_materno = models.CharField(max_length=25, blank=True, null=True)
    email = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendedor'
        managed = False

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"


class DocumentoTributario(models.Model):
    documento_id = models.BigAutoField(primary_key=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=50)  # enum tipo_documento
    folio = models.IntegerField(blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    subtotal = models.IntegerField()
    total = models.IntegerField()
    rut_cliente = models.CharField(max_length=12, blank=True, null=True)
    nombre_cliente = models.CharField(max_length=45, blank=True, null=True)
    rut_empresa = models.CharField(max_length=12, blank=True, null=True)
    razon_social = models.CharField(max_length=100, blank=True, null=True)
    giro = models.CharField(max_length=255, blank=True, null=True)
    direccion_facturacion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'documento_tributario'
        managed = False
        constraints = [
            models.CheckConstraint(check=Q(subtotal__gte=0), name='documento_tributario_subtotal_check'),
            models.CheckConstraint(check=Q(total__gte=0), name='documento_tributario_total_check'),
            models.CheckConstraint(
                check=(~Q(tipo_documento='boleta') | (Q(rut_cliente__isnull=False) & Q(nombre_cliente__isnull=False))),
                name='chk_boleta_campos'
            ),
            models.CheckConstraint(
                check=(~Q(tipo_documento='factura') | (Q(rut_empresa__isnull=False) & Q(razon_social__isnull=False) & Q(giro__isnull=False))),
                name='chk_factura_campos'
            ),
        ]
        indexes = [
            models.Index(fields=['pedido'], name='idx_documento_pedido'),
        ]

    def __str__(self):
        return f"DocTrib {self.documento_id} ({self.tipo_documento})"


class MovimientoEstado(models.Model):
    movimiento_estado_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=50)  # enum estado_producto
    estado_actual = models.CharField(max_length=50)    # enum estado_producto

    class Meta:
        db_table = 'movimiento_estado'
        managed = False
        constraints = [
            models.CheckConstraint(check=~Q(estado_anterior=models.F('estado_actual')), name='chk_cambio_estado')
        ]

    def __str__(self):
        return f"MovEstado {self.movimiento_estado_id}"


class MovimientoStock(models.Model):
    movimiento_stock_id = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    tipo_operacion = models.CharField(max_length=50)  # enum tipo_operacion

    class Meta:
        db_table = 'movimiento_stock'
        managed = False
        indexes = [
            models.Index(fields=['fecha_movimiento'], name='idx_movimiento_stock_fecha'),
            models.Index(fields=['producto'], name='idx_movimiento_stock_producto'),
        ]

    def __str__(self):
        return f"MovStock {self.movimiento_stock_id}"


class Pago(models.Model):
    pago_id = models.BigAutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    monto = models.IntegerField()
    metodo = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    transbank_token = models.CharField(max_length=50, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pago'
        managed = False
        constraints = [
            models.CheckConstraint(check=Q(monto__gt=0), name='pago_monto_check'),
        ]
        indexes = [
            models.Index(fields=['pedido'], name='idx_pago_pedido'),
        ]

    def __str__(self):
        return f"Pago {self.pago_id} ({self.monto})"


class PedidoItem(models.Model):
    pedido_item_id = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    cantidad = models.IntegerField()
    precio_unitario = models.IntegerField()
    subtotal = models.IntegerField()

    class Meta:
        db_table = 'pedido_item'
        managed = False
        constraints = [
            models.CheckConstraint(check=Q(cantidad__gt=0), name='pedido_item_cantidad_check'),
            models.CheckConstraint(check=Q(precio_unitario__gte=0), name='pedido_item_precio_unitario_check'),
            models.CheckConstraint(check=Q(subtotal__gte=0), name='pedido_item_subtotal_check'),
        ]

    def __str__(self):
        return f"PedidoItem {self.pedido_item_id}"
