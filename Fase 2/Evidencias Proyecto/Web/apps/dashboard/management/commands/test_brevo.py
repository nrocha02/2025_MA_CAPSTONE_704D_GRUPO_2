from django.core.management.base import BaseCommand
from apps.ventas.models import ClientePersona, Producto
from apps.ventas.brevo_service import BrevoEmailService


class Command(BaseCommand):
    help = 'Comando para probar la funcionalidad de Brevo Email Service'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Probar conexión con API de Brevo',
        )
        parser.add_argument(
            '--send-welcome',
            type=str,
            help='Enviar email de bienvenida a un cliente (proporcionar email)',
        )
        parser.add_argument(
            '--send-stock-alert',
            type=str,
            help='Enviar alerta de stock bajo (proporcionar email admin)',
        )
        parser.add_argument(
            '--send-custom',
            action='store_true',
            help='Enviar email personalizado de prueba',
        )

    def handle(self, *args, **options):
        brevo_service = BrevoEmailService()
        
        if options['test_connection']:
            self.stdout.write(self.style.SUCCESS('🔌 Probando conexión con Brevo API...'))
            result = brevo_service.get_account_info()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS('✅ Conexión exitosa con Brevo API')
                )
                self.stdout.write(f"API Key configurada: {brevo_service.api_key[:20]}...")
                self.stdout.write(f"Email configurado: {brevo_service.sender_email}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error de conexión: {result["message"]}')
                )
        
        if options['send_welcome']:
            email = options['send_welcome']
            self.stdout.write(f'📧 Enviando email de bienvenida a {email}...')
            
            try:
                # Buscar cliente en la base de datos
                cliente = ClientePersona.objects.filter(email=email).first()
                if cliente:
                    nombre = f"{cliente.nombres} {cliente.apellido_paterno}"
                else:
                    nombre = "Cliente de Prueba"
                
                result = brevo_service.send_welcome_email(
                    cliente_email=email,
                    cliente_nombre=nombre
                )
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Email de bienvenida enviado exitosamente a {email}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error al enviar email: {result["message"]}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error inesperado: {str(e)}')
                )
        
        if options['send_stock_alert']:
            admin_email = options['send_stock_alert']
            self.stdout.write(f'⚠️ Enviando alerta de stock bajo a {admin_email}...')
            
            try:
                # Obtener productos con stock bajo
                productos_bajo_stock = Producto.objects.filter(
                    stock__lt=10, 
                    estado_producto='activo'
                ).select_related('categoria')
                
                if not productos_bajo_stock.exists():
                    self.stdout.write(
                        self.style.WARNING('ℹ️ No hay productos con stock bajo en este momento')
                    )
                    return
                
                # Preparar datos para el email
                productos_data = []
                for producto in productos_bajo_stock:
                    productos_data.append({
                        'nombre': producto.nombre,
                        'sku': producto.sku,
                        'stock': producto.stock,
                        'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría'
                    })
                
                result = brevo_service.send_stock_alert(
                    admin_email=admin_email,
                    productos_bajo_stock=productos_data
                )
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Alerta de stock enviada exitosamente a {admin_email}')
                    )
                    self.stdout.write(f'📊 Productos alertados: {len(productos_data)}')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error al enviar alerta: {result["message"]}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error inesperado: {str(e)}')
                )
        
        if options['send_custom']:
            self.stdout.write('📝 Enviando email personalizado de prueba...')
            
            try:
                result = brevo_service.send_custom_email(
                    recipient_email="cordillerapetschile@gmail.com",
                    recipient_name="Usuario de Prueba",
                    subject="🧪 Email de Prueba desde Django - Cordillera Pets",
                    message="""
                    <h2>¡Email de Prueba Exitoso! 🎉</h2>
                    
                    <p>Este es un email de prueba enviado desde el comando de Django usando Brevo API.</p>
                    
                    <p><strong>Características probadas:</strong></p>
                    <ul>
                        <li>✅ Conexión con Brevo API</li>
                        <li>✅ Envío de emails HTML</li>
                        <li>✅ Configuración desde Django</li>
                        <li>✅ Integración con modelos de Django</li>
                    </ul>
                    
                    <p>¡Todo funciona correctamente!</p>
                    
                    <p><em>Enviado desde: Sistema de gestión Cordillera Pets</em></p>
                    """
                )
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Email personalizado enviado exitosamente')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error al enviar email: {result["message"]}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error inesperado: {str(e)}')
                )
        
        if not any([options['test_connection'], options['send_welcome'], 
                   options['send_stock_alert'], options['send_custom']]):
            self.stdout.write(self.style.WARNING('ℹ️ No se especificó ninguna acción. Usa --help para ver las opciones disponibles.'))
            self.stdout.write('')
            self.stdout.write('Ejemplos de uso:')
            self.stdout.write('  python manage.py test_brevo --test-connection')
            self.stdout.write('  python manage.py test_brevo --send-welcome usuario@ejemplo.com')
            self.stdout.write('  python manage.py test_brevo --send-stock-alert admin@ejemplo.com')
            self.stdout.write('  python manage.py test_brevo --send-custom')