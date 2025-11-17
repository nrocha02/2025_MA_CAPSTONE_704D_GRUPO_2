from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.ventas.models import Producto
from apps.ventas.brevo_service import BrevoEmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Job diario para enviar alertas de stock bajo a las 10 AM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='cordillerapetschile@gmail.com',
            help='Email del administrador para recibir las alertas',
        )
        parser.add_argument(
            '--stock-minimo',
            type=int,
            default=10,
            help='Nivel mínimo de stock para generar alerta',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué productos se alertarían, sin enviar emails',
        )

    def handle(self, *args, **options):
        admin_email = options['admin_email']
        stock_minimo = options['stock_minimo']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'=== JOB DIARIO DE STOCK - {timezone.now().strftime("%d/%m/%Y %H:%M:%S")} ===')
        )
        
        try:
            # Obtener productos con stock bajo
            productos_bajo_stock = Producto.objects.filter(
                stock__lt=stock_minimo,
                estado_producto='activo'
            ).select_related('categoria', 'marca').order_by('stock', 'nombre')
            
            if not productos_bajo_stock.exists():
                self.stdout.write(
                    self.style.SUCCESS('✓ No hay productos con stock bajo. Todo está en orden.')
                )
                logger.info("Job diario de stock: No hay productos con stock bajo")
                return
            
            # Preparar datos para el reporte
            productos_data = []
            productos_criticos = 0  # Stock <= 3
            productos_bajos = 0     # Stock 4-9
            
            for producto in productos_bajo_stock:
                if producto.stock <= 3:
                    productos_criticos += 1
                else:
                    productos_bajos += 1
                    
                productos_data.append({
                    'nombre': producto.nombre,
                    'sku': producto.sku,
                    'stock': producto.stock,
                    'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
                    'marca': producto.marca.nombre if producto.marca else 'Sin marca',
                    'precio': producto.precio
                })
            
            # Mostrar resumen
            self.stdout.write(f'📊 RESUMEN DE STOCK:')
            self.stdout.write(f'   • Productos críticos (≤3): {productos_criticos}')
            self.stdout.write(f'   • Productos bajos (4-9): {productos_bajos}')
            self.stdout.write(f'   • Total productos alertados: {len(productos_data)}')
            
            # Mostrar detalle de productos
            self.stdout.write('\n📦 PRODUCTOS CON STOCK BAJO:')
            for producto in productos_data:
                nivel = "CRÍTICO" if producto['stock'] <= 3 else "BAJO"
                self.stdout.write(
                    f'   • {producto["nombre"]} ({producto["sku"]}) - Stock: {producto["stock"]} [{nivel}]'
                )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'\n🧪 DRY RUN: No se enviará email (usar sin --dry-run para enviar)')
                )
                return
            
            # Enviar alerta por email
            self.stdout.write(f'\n📧 Enviando alerta a {admin_email}...')
            
            brevo_service = BrevoEmailService()
            result = brevo_service.send_stock_alert_job(
                admin_email=admin_email,
                productos_bajo_stock=productos_data,
                productos_criticos=productos_criticos,
                productos_bajos=productos_bajos
            )
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Alerta enviada exitosamente a {admin_email}')
                )
                logger.info(f"Job diario de stock: Alerta enviada a {admin_email} - {len(productos_data)} productos")
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error al enviar alerta: {result["message"]}')
                )
                logger.error(f"Job diario de stock: Error al enviar alerta - {result['message']}")
                
        except Exception as e:
            error_msg = f"Error en job diario de stock: {str(e)}"
            self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))
            logger.error(error_msg, exc_info=True)
            
            # Intentar enviar email de error
            try:
                brevo_service = BrevoEmailService()
                brevo_service.send_job_error_alert(admin_email, error_msg)
            except:
                pass  # Si no se puede enviar el email de error, solo loggeamos
        
        self.stdout.write(
            self.style.SUCCESS(f'=== FIN JOB DIARIO DE STOCK ===\n')
        )