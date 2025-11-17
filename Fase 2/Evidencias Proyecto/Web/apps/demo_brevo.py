#!/usr/bin/env python3
"""
Script de demostración para la integración de Brevo con Cordillera Pets
Ejecutar: python demo_brevo.py
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import sys
import os


class BrevoDemo:
    def __init__(self):
        self.api_key = os.getenv('KEY_BREVO', '')
        self.sender_email = "cordillerapetschile@gmail.com"
        self.sender_name = "Cordillera Pets"
        
        # Configurar cliente API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    def test_connection(self):
        """Probar conexión con Brevo API"""
        print("=" * 50)
        print("PROBANDO CONEXIÓN CON BREVO API")
        print("=" * 50)
        
        try:
            account_api = sib_api_v3_sdk.AccountApi(
                sib_api_v3_sdk.ApiClient(sib_api_v3_sdk.Configuration())
            )
            account_api.api_client.configuration.api_key['api-key'] = self.api_key
            
            account_info = account_api.get_account()
            print("✓ Conexión exitosa")
            print(f"  Email: {account_info.email}")
            print(f"  Nombre: {account_info.first_name} {account_info.last_name}")
            print(f"  Plan: {account_info.plan[0].type}")
            return True
            
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            return False
    
    def send_welcome_email(self, email="cordillerapetschile@gmail.com"):
        """Enviar email de bienvenida"""
        print("\n" + "=" * 50)
        print("ENVIANDO EMAIL DE BIENVENIDA")
        print("=" * 50)
        
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": email, "name": "Cliente de Prueba"}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject="¡Bienvenido a Cordillera Pets!",
                html_content="""
                <html>
                <head></head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c5aa0;">¡Hola Cliente de Prueba!</h2>
                        <p>¡Bienvenido a Cordillera Pets! Nos complace tenerte como parte de nuestra comunidad.</p>
                        
                        <h3 style="color: #2c5aa0;">En nuestra tienda encontrarás:</h3>
                        <ul>
                            <li>🐕 Alimento premium para perros y gatos</li>
                            <li>🎾 Juguetes y accesorios</li>
                            <li>🛁 Productos de cuidado e higiene</li>
                            <li>🏠 Casitas y camas</li>
                            <li>🥇 Y mucho más...</li>
                        </ul>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>¡Oferta especial de bienvenida!</strong></p>
                            <p>Usa el código <strong>BIENVENIDO10</strong> y obtén un 10% de descuento en tu primera compra.</p>
                        </div>
                        
                        <p>¡Esperamos que disfrutes de tu experiencia de compra con nosotros!</p>
                        
                        <br>
                        <p>Saludos cordiales,<br>
                        <strong>El equipo de Cordillera Pets</strong></p>
                        
                        <hr style="margin: 30px 0;">
                        <p style="font-size: 12px; color: #666;">
                            📧 cordillerapetschile@gmail.com | 📞 +56999999999 | 🌐 www.cordillerapets.cl
                        </p>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            print(f"✓ Email de bienvenida enviado a {email}")
            print(f"  Message ID: {api_response.message_id}")
            return True
            
        except Exception as e:
            print(f"✗ Error al enviar email: {e}")
            return False
    
    def send_order_confirmation(self, email="cordillerapetschile@gmail.com"):
        """Enviar confirmación de pedido simulada"""
        print("\n" + "=" * 50)
        print("ENVIANDO CONFIRMACIÓN DE PEDIDO")
        print("=" * 50)
        
        # Datos simulados del pedido
        pedido_id = 99999
        items = [
            {"nombre": "Alimento Premium Perro Adulto 15kg", "cantidad": 1, "precio": 25000},
            {"nombre": "Juguete Kong Classic", "cantidad": 2, "precio": 8500},
            {"nombre": "Shampoo para Mascotas 500ml", "cantidad": 1, "precio": 12000},
        ]
        total = sum(item["precio"] * item["cantidad"] for item in items)
        
        # Generar tabla de productos
        items_html = ""
        for item in items:
            subtotal = item["precio"] * item["cantidad"]
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['nombre']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{item['cantidad']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item['precio']:,}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${subtotal:,}</td>
            </tr>
            """
        
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": email, "name": "Cliente de Prueba"}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=f"Confirmación de Pedido #{pedido_id} - Cordillera Pets",
                html_content=f"""
                <html>
                <head></head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c5aa0;">¡Gracias por tu compra, Cliente de Prueba!</h2>
                        <p>Tu pedido ha sido confirmado y está siendo procesado.</p>
                        
                        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin: 0; color: #1976d2;">Detalles del Pedido #{pedido_id}</h3>
                        </div>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                            <thead>
                                <tr style="background-color: #f5f5f5;">
                                    <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #ddd;">Producto</th>
                                    <th style="padding: 12px 8px; text-align: center; border-bottom: 2px solid #ddd;">Cantidad</th>
                                    <th style="padding: 12px 8px; text-align: right; border-bottom: 2px solid #ddd;">Precio Unit.</th>
                                    <th style="padding: 12px 8px; text-align: right; border-bottom: 2px solid #ddd;">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                        </table>
                        
                        <div style="text-align: right; font-size: 18px; font-weight: bold; margin: 20px 0;">
                            <span style="background-color: #4caf50; color: white; padding: 10px 20px; border-radius: 5px;">
                                Total: ${total:,}
                            </span>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p><strong>📦 Estado del pedido:</strong> Confirmado</p>
                            <p><strong>🚚 Tiempo estimado de entrega:</strong> 2-3 días hábiles</p>
                            <p><strong>📧 Te notificaremos cuando tu pedido sea enviado.</strong></p>
                        </div>
                        
                        <br>
                        <p>Saludos cordiales,<br>
                        <strong>El equipo de Cordillera Pets</strong></p>
                        
                        <hr style="margin: 30px 0;">
                        <p style="font-size: 12px; color: #666;">
                            📧 cordillerapetschile@gmail.com | 📞 +56999999999 | 🌐 www.cordillerapets.cl
                        </p>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            print(f"✓ Confirmación de pedido enviada a {email}")
            print(f"  Pedido ID: {pedido_id}")
            print(f"  Total: ${total:,}")
            print(f"  Message ID: {api_response.message_id}")
            return True
            
        except Exception as e:
            print(f"✗ Error al enviar confirmación: {e}")
            return False
    
    def send_stock_alert(self, admin_email="cordillerapetschile@gmail.com"):
        """Enviar alerta de stock bajo"""
        print("\n" + "=" * 50)
        print("ENVIANDO ALERTA DE STOCK BAJO")
        print("=" * 50)
        
        # Datos simulados de productos con stock bajo
        productos_bajo_stock = [
            {"nombre": "Alimento Premium Gato Adulto 7kg", "sku": "CAT-PREM-7K", "stock": 3, "categoria": "Alimentos"},
            {"nombre": "Collar Antipulgas Mediano", "sku": "COL-AP-MED", "stock": 5, "categoria": "Accesorios"},
            {"nombre": "Arena Silica Gel 5kg", "sku": "ARE-SIL-5K", "stock": 2, "categoria": "Higiene"},
            {"nombre": "Juguete Cuerda Perro Grande", "sku": "JUG-CUE-GRA", "stock": 8, "categoria": "Juguetes"},
        ]
        
        # Generar tabla de productos
        productos_html = ""
        for producto in productos_bajo_stock:
            color = "#dc3545" if producto["stock"] <= 3 else "#ffc107"
            productos_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{producto['nombre']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;"><code>{producto['sku']}</code></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">
                    <span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold;">
                        {producto['stock']}
                    </span>
                </td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{producto['categoria']}</td>
            </tr>
            """
        
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email, "name": "Administrador"}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject="🚨 Alerta: Productos con Stock Bajo - Cordillera Pets",
                html_content=f"""
                <html>
                <head></head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                            <h2 style="margin: 0;">⚠️ ALERTA DE STOCK BAJO</h2>
                        </div>
                        
                        <p>Los siguientes productos tienen stock bajo y requieren <strong>reposición urgente</strong>:</p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                            <thead>
                                <tr style="background-color: #f5f5f5;">
                                    <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #ddd;">Producto</th>
                                    <th style="padding: 12px 8px; text-align: center; border-bottom: 2px solid #ddd;">SKU</th>
                                    <th style="padding: 12px 8px; text-align: center; border-bottom: 2px solid #ddd;">Stock</th>
                                    <th style="padding: 12px 8px; text-align: left; border-bottom: 2px solid #ddd;">Categoría</th>
                                </tr>
                            </thead>
                            <tbody>
                                {productos_html}
                            </tbody>
                        </table>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p><strong>📋 Recomendaciones:</strong></p>
                            <ul>
                                <li>Revisar y reponer stock de estos productos lo antes posible</li>
                                <li>Contactar a proveedores para acelerar entregas</li>
                                <li>Considerar ajustar niveles mínimos de stock</li>
                            </ul>
                        </div>
                        
                        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>📊 Estadísticas:</strong></p>
                            <p>Total de productos alertados: <strong>{len(productos_bajo_stock)}</strong></p>
                            <p>Fecha de alerta: <strong>{__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}</strong></p>
                        </div>
                        
                        <br>
                        <p>Sistema de gestión - <strong>Cordillera Pets</strong></p>
                        
                        <hr style="margin: 30px 0;">
                        <p style="font-size: 12px; color: #666;">
                            Este es un mensaje automático del sistema de gestión de inventario.
                        </p>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            print(f"✓ Alerta de stock enviada a {admin_email}")
            print(f"  Productos alertados: {len(productos_bajo_stock)}")
            print(f"  Message ID: {api_response.message_id}")
            return True
            
        except Exception as e:
            print(f"✗ Error al enviar alerta: {e}")
            return False


def main():
    print("DEMO - INTEGRACIÓN BREVO CON CORDILLERA PETS")
    print("=" * 60)
    
    demo = BrevoDemo()
    
    # 1. Probar conexión
    if not demo.test_connection():
        print("Error: No se pudo conectar con Brevo API")
        sys.exit(1)
    
    # 2. Enviar email de bienvenida
    demo.send_welcome_email()
    
    # 3. Enviar confirmación de pedido
    demo.send_order_confirmation()
    
    # 4. Enviar alerta de stock
    demo.send_stock_alert()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("Revisa tu bandeja de entrada (cordillerapetschile@gmail.com)")
    print("También revisa la carpeta de spam si no ves los emails")


if __name__ == "__main__":
    main()