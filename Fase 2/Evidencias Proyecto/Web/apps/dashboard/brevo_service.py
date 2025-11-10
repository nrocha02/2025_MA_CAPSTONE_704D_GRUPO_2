import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import logging
import os

# Configurar logger
logger = logging.getLogger(__name__)

class BrevoEmailService:
    #Servicio para gestionar envío de correos electrónicos con Brevo"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'BREVO_API_KEY', os.getenv('KEY_BREVO', ''))
        self.sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', "cordillerapetschile@gmail.com")
        self.sender_name = getattr(settings, 'BREVO_SENDER_NAME', "Cordillera Pets")
        
        # Configurar cliente API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    def send_welcome_email(self, cliente_email, cliente_nombre):
        #Enviar correo de bienvenida a nuevo cliente"""
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": cliente_email, "name": cliente_nombre}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject="¡Bienvenido a Cordillera Pets!",
                html_content=f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: 'Arial', sans-serif;
                            background-color: #f8f9fa;
                            color: #333;
                            padding: 0;
                            margin: 0;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 40px auto;
                            background-color: #ffffff;
                            border-radius: 12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                            overflow: hidden;
                        }}
                        .header {{
                            background-color: #000000;
                            text-align: center;
                            padding: 20px;
                        }}
                        .header img {{
                            width: 160px;
                        }}
                        .content {{
                            padding: 30px 40px;
                            text-align: left;
                        }}
                        h2 {{
                            color: #E6392D;
                        }}
                        ul {{
                            list-style: none;
                            padding-left: 0;
                        }}
                        ul li::before {{
                            content: "🐾 ";
                            color: #1C4E80;
                        }}
                        .button {{
                            background-color: #E6392D;
                            color: white;
                            padding: 12px 20px;
                            text-decoration: none;
                            border-radius: 6px;
                            display: inline-block;
                            margin-top: 15px;
                        }}
                        .button:hover {{
                            background-color: #1C4E80;
                        }}
                        .footer {{
                            background-color: #1C4E80;
                            color: white;
                            text-align: center;
                            padding: 15px;
                            font-size: 13px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <img src="static/img/logo.png" alt="Cordillera Pets">
                        </div>
                        <div class="content">
                            <h2>¡Hola {cliente_nombre}!</h2>
                            <p>Nos alegra darte la bienvenida a <strong>Cordillera Pets</strong> 🐶🐱</p>
                            <p>En nuestra tienda encontrarás los mejores productos para tus mascotas:</p>
                            <ul>
                                <li>Alimentos premium para perros y gatos</li>
                                <li>Arenas sanitarias para gatos</li>
                                <li>Productos de cuidado e higiene</li>
                                <li>Juguetes y accesorios </li>
                                <li>Y mucho más...</li>
                            </ul>
                            <a href="https://cordillerapets.cl" class="button">Visitar tienda</a>
                            <p style="margin-top: 25px;">Gracias por confiar en nosotros 💚<br>Tu equipo de <strong>Cordillera Pets</strong></p>
                        </div>
                        <div class="footer">
                            © 2025 Cordillera Pets · Alimentos, arenas sanitarias y accesorios para mascotas    
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email de bienvenida enviado exitosamente: {api_response}")
            return {"success": True, "message": "Email enviado exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar email de bienvenida: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}
    
    def send_order_confirmation(self, cliente_email, cliente_nombre, pedido_id, total, items):
        #Enviar correo de confirmación de pedido"""
        try:
            # Generar lista de productos
            items_html = ""
            for item in items:
                items_html += f"""
                <tr>
                    <td>{item['nombre']}</td>
                    <td>{item['cantidad']}</td>
                    <td>${item['precio_unitario']:,}</td>
                    <td>${item['subtotal']:,}</td>
                </tr>
                """
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": cliente_email, "name": cliente_nombre}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=f"Confirmación de Pedido #{pedido_id} - Cordillera Pets",
                html_content=f"""
                <html>
                <head>
                    <style>
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h2>¡Gracias por tu compra, {cliente_nombre}!</h2>
                    <p>Tu pedido ha sido confirmado y está siendo procesado.</p>
                    
                    <h3>Detalles del Pedido #{pedido_id}</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Cantidad</th>
                                <th>Precio Unitario</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <h3>Total: ${total:,}</h3>
                    
                    <p>Te notificaremos cuando tu pedido sea enviado.</p>
                    
                    <br>
                    <p>Saludos cordiales,<br>
                    El equipo de Cordillera Pets</p>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email de confirmación de pedido enviado: {api_response}")
            return {"success": True, "message": "Email enviado exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar email de confirmación: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}
        
    def pedido_entregado(self, cliente_email, cliente_nombre, pedido_id, total, items):
        #Enviar correo de confirmación de entrega de pedido"""
        try:
            # Generar lista de productos
            items_html = ""
            for item in items:
                items_html += f"""
                <tr>
                    <td>{item['nombre']}</td>
                    <td>{item['cantidad']}</td>
                    <td>${item['precio_unitario']:,}</td>
                    <td>${item['subtotal']:,}</td>
                </tr>
                """
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": cliente_email, "name": cliente_nombre}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=f"Confirmación de Entrega de Pedido #{pedido_id} - Cordillera Pets",
                html_content=f"""
                <html>
                <head>
                    <style>
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h2>¡Gracias por tu compra, {cliente_nombre}!</h2>
                    <p>Tu pedido ha sido entregado satisfactoriamente.</p>
                    
                    <h3>Detalles del Pedido #{pedido_id}</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Cantidad</th>
                                <th>Precio Unitario</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <h3>Total: ${total:,}</h3>
                    
                    <p>Muchas Gracias Por su compra.</p>
                    
                    <br>
                    <p>Saludos cordiales,<br>
                    El equipo de Cordillera Pets</p>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email de entrega de pedido enviado: {api_response}")
            return {"success": True, "message": "Email enviado exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar email de entrega: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}
    
    def send_stock_alert(self, admin_email, productos_bajo_stock):
        #Enviar alerta de stock bajo a administradores"""
        try:
            productos_html = ""
            for producto in productos_bajo_stock:
                productos_html += f"""
                <tr>
                    <td>{producto['nombre']}</td>
                    <td>{producto['sku']}</td>
                    <td>{producto['stock']}</td>
                    <td>{producto['categoria']}</td>
                </tr>
                """
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject="🚨 Alerta: Productos con Stock Bajo - Cordillera Pets",
                html_content=f"""
                <html>
                <head>
                    <style>
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #ffebee; }}
                        .alert {{ color: #d32f2f; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <h2 class="alert">⚠️ Alerta de Stock Bajo</h2>
                    <p>Los siguientes productos tienen stock bajo y requieren reposición:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>SKU</th>
                                <th>Stock Actual</th>
                                <th>Categoría</th>
                            </tr>
                        </thead>
                        <tbody>
                            {productos_html}
                        </tbody>
                    </table>
                    
                    <p><strong>Recomendación:</strong> Revisar y reponer stock de estos productos lo antes posible.</p>
                    
                    <br>
                    <p>Sistema de gestión - Cordillera Pets</p>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Alerta de stock bajo enviada: {api_response}")
            return {"success": True, "message": "Alerta enviada exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar alerta de stock: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar alerta: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}
    

    
    def send_stock_alert_job(self, admin_email, productos_bajo_stock, productos_criticos=0, productos_bajos=0):
        #Enviar alerta de stock bajo desde job diario con template mejorado"""
        try:
            from datetime import datetime
            
            # Generar tabla de productos con colores según criticidad
            productos_html = ""
            for producto in productos_bajo_stock:
                if producto['stock'] <= 3:
                    color_class = "background-color: #ffebee; color: #c62828;"
                    nivel = "CRÍTICO"
                    icono = "🔴"
                elif producto['stock'] <= 5:
                    color_class = "background-color: #fff3e0; color: #f57c00;"
                    nivel = "MUY BAJO"
                    icono = "🟠"
                else:
                    color_class = "background-color: #fffde7; color: #f9a825;"
                    nivel = "BAJO"
                    icono = "🟡"
                    
                productos_html += f"""
                <tr style="{color_class}">
                    <td>{icono} {producto['nombre']}</td>
                    <td><code>{producto['sku']}</code></td>
                    <td style="font-weight: bold; text-align: center;">{producto['stock']}</td>
                    <td>{nivel}</td>
                    <td>{producto['categoria']}</td>
                    <td>${producto['precio']:,}</td>
                </tr>
                """
            
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email, "name": "Administrador"}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=f"🚨 REPORTE DIARIO DE STOCK - {len(productos_bajo_stock)} productos requieren atención",
                html_content=f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #d32f2f, #f44336); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
                        .summary {{ background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }}
                        .critical {{ background-color: #ffebee; border-left-color: #f44336; }}
                        .warning {{ background-color: #fff3e0; border-left-color: #ff9800; }}
                        .table-container {{ overflow-x: auto; }}
                        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                        th {{ background: linear-gradient(135deg, #37474f, #455a64); color: white; padding: 12px 8px; text-align: left; }}
                        td {{ padding: 10px 8px; border-bottom: 1px solid #e0e0e0; }}
                        .footer {{ background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 12px; color: #666; }}
                        .priority-high {{ animation: blink 2s infinite; }}
                        @keyframes blink {{ 0%, 50% {{ opacity: 1; }} 25%, 75% {{ opacity: 0.5; }} }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🚨 REPORTE DIARIO DE STOCK</h1>
                            <p>Cordillera Pets - Sistema de Gestión de Inventario</p>
                            <p><strong>Fecha:</strong> {fecha_actual}</p>
                        </div>
                        
                        <div class="summary">
                            <h3>📊 RESUMEN EJECUTIVO</h3>
                            <div style="display: flex; justify-content: space-around; text-align: center; margin: 15px 0;">
                                <div>
                                    <div style="font-size: 2em; font-weight: bold; color: #d32f2f;">{productos_criticos}</div>
                                    <div>Productos Críticos (≤3)</div>
                                </div>
                                <div>
                                    <div style="font-size: 2em; font-weight: bold; color: #ff9800;">{productos_bajos}</div>
                                    <div>Productos Bajos (4-9)</div>
                                </div>
                                <div>
                                    <div style="font-size: 2em; font-weight: bold; color: #2196f3;">{len(productos_bajo_stock)}</div>
                                    <div>Total Alertados</div>
                                </div>
                            </div>
                        </div>
                        
                        {f'<div class="summary critical priority-high"><h4>⚠️ ATENCIÓN URGENTE</h4><p>Hay {productos_criticos} productos en estado CRÍTICO que requieren reposición inmediata para evitar desabastecimiento.</p></div>' if productos_criticos > 0 else ''}
                        
                        <h3>📦 DETALLE DE PRODUCTOS</h3>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Producto</th>
                                        <th>SKU</th>
                                        <th>Stock</th>
                                        <th>Nivel</th>
                                        <th>Categoría</th>
                                        <th>Precio</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {productos_html}
                                </tbody>
                            </table>
                        </div>
                        
                        <div class="summary">
                            <h4>📋 ACCIONES RECOMENDADAS</h4>
                            <ul>
                                <li><strong>Inmediato:</strong> Contactar proveedores para productos críticos (≤3 unidades)</li>
                                <li><strong>Esta semana:</strong> Programar reposición de productos con stock bajo</li>
                            </ul>
                        </div>
                        
                        <div class="summary warning">
                            <h4>💡 RECORDATORIO</h4>
                            <p>Este reporte se genera automáticamente cada día a las <strong>10:00 AM</strong>. Para cambiar la configuración o recibir alertas adicionales, contacta al equipo de TI.</p>
                        </div>
                        
                        <div class="footer">
                            <p><strong>Sistema de Gestión de Inventario - Cordillera Pets</strong></p>
                            <p>📧 Reportes automáticos | 🤖 Generado por: Job Diario de Stock | 🕐 Próximo reporte: mañana 10:00 AM</p>
                            <p>Para soporte técnico contactar: cordillerapetschile@gmail.com</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Reporte diario de stock enviado: {api_response}")
            return {"success": True, "message": "Reporte enviado exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar reporte de stock: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar reporte: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}
    
    def send_job_error_alert(self, admin_email, error_message):
        #Enviar alerta de error en job automático"""
        try:
            from datetime import datetime
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email, "name": "Administrador"}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject="🚨 ERROR EN JOB AUTOMÁTICO - Cordillera Pets",
                html_content=f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .error-header {{ background-color: #d32f2f; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                        .error-details {{ background-color: #ffebee; padding: 15px; border-left: 4px solid #f44336; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-header">
                            <h2>🚨 ERROR EN SISTEMA AUTOMÁTICO</h2>
                            <p>Job diario de stock falló</p>
                        </div>
                        
                        <div class="error-details">
                            <h3>📋 Detalles del Error</h3>
                            <p><strong>Fecha/Hora:</strong> {fecha_actual}</p>
                            <p><strong>Job:</strong> Reporte diario de stock</p>
                            <p><strong>Error:</strong></p>
                            <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px;">{error_message}</pre>
                        </div>
                        
                        <p><strong>⚠️ Acción Requerida:</strong></p>
                        <ul>
                            <li>Verificar el sistema y corregir el error</li>
                            <li>Ejecutar manualmente el reporte de stock si es necesario</li>
                            <li>Revisar logs del servidor para más detalles</li>
                        </ul>
                        
                        <p>Sistema de monitoreo - Cordillera Pets</p>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Alerta de error de job enviada: {api_response}")
            return {"success": True, "message": "Alerta de error enviada", "response": api_response}
            
        except Exception as e:
            logger.error(f"Error al enviar alerta de error: {e}")
            return {"success": False, "message": f"Error: {e}"}
    
    def get_account_info(self):
        #Obtener información de la cuenta de Brevo"""
        try:
            account_api = sib_api_v3_sdk.AccountApi(
                sib_api_v3_sdk.ApiClient(sib_api_v3_sdk.Configuration())
            )
            account_api.api_client.configuration.api_key['api-key'] = self.api_key
            
            api_response = account_api.get_account()
            return {"success": True, "data": api_response}
            
        except ApiException as e:
            logger.error(f"Error al obtener info de cuenta: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}

    def send_custom_email(self, recipient_email, recipient_name, subject, message):
        #Enviar correo personalizado"""
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": recipient_email, "name": recipient_name}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=subject,
                html_content=f"""
                <html>
                <head></head>
                <body>
                    <h2>Cordillera Pets</h2>
                    <div>{message}</div>
                    <br>
                    <p>Saludos cordiales,<br>
                    El equipo de Cordillera Pets</p>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email personalizado enviado: {api_response}")
            return {"success": True, "message": "Email enviado exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar email personalizado: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}

def send_recovery_email(self, cliente_email):
        #Enviar correo de recuperacion de contraseña"""
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": cliente_email}],
                sender={"name": self.sender_name, "email": self.sender_email},
                subject="¡Bienvenido a Cordillera Pets!",
                html_content=f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: 'Arial', sans-serif;
                            background-color: #f8f9fa;
                            color: #333;
                            padding: 0;
                            margin: 0;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 40px auto;
                            background-color: #ffffff;
                            border-radius: 12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                            overflow: hidden;
                        }}
                        .header {{
                            background-color: #000000;
                            text-align: center;
                            padding: 20px;
                        }}
                        .header img {{
                            width: 160px;
                        }}
                        .content {{
                            padding: 30px 40px;
                            text-align: left;
                        }}
                        h2 {{
                            color: #E6392D;
                        }}
                        ul {{
                            list-style: none;
                            padding-left: 0;
                        }}
                        ul li::before {{
                            content: "🐾 ";
                            color: #1C4E80;
                        }}
                        .button {{
                            background-color: #E6392D;
                            color: white;
                            padding: 12px 20px;
                            text-decoration: none;
                            border-radius: 6px;
                            display: inline-block;
                            margin-top: 15px;
                        }}
                        .button:hover {{
                            background-color: #1C4E80;
                        }}
                        .footer {{
                            background-color: #1C4E80;
                            color: white;
                            text-align: center;
                            padding: 15px;
                            font-size: 13px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <img src="../static/img/logo.png" alt="Cordillera Pets">
                        </div>
                        <div class="content">
                            <p>Recupera tu contraseña> 🐶🐱</p>
                            <p>En nuestra tienda encontrarás los mejores productos para tus mascotas:</p>
                            <a href="https://cordillerapets.cl" class="button">Cambiar contraseña</a>
                            <p style="margin-top: 25px;">Gracias por confiar en nosotros 💚<br>Tu equipo de <strong>Cordillera Pets</strong></p>
                        </div>
                        <div class="footer">
                            © 2025 Cordillera Pets · Alimentos, arenas sanitarias y accesorios para mascotas    
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email de recuperación enviado exitosamente: {api_response}")
            return {"success": True, "message": "Email enviado exitosamente", "response": api_response}
            
        except ApiException as e:
            logger.error(f"Error al enviar email de recuperación: {e}")
            return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}

