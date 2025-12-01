import hashlib
import json
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as login_aut
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .brevo_service import BrevoEmailService
from .models import *
from ..ventas.utils import validar_rut, formatear_rut
from .tokens import cliente_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
import hashlib

# Configurar logger
logger = logging.getLogger(__name__)


# Vistas de páginas legales
def terminos_condiciones(request):
    """Vista para la página de Términos y Condiciones"""
    return render(request, "ventas/terminos_condiciones.html")


def politica_privacidad(request):
    """Vista para la página de Política de Privacidad"""
    return render(request, "ventas/politica_privacidad.html")


def politica_devoluciones(request):
    """Vista para la página de Política de Devoluciones"""
    return render(request, "ventas/politica_devoluciones.html")


def index(request):
    # Obtener productos recomendados (los primeros 8 productos activos)
    productos_recomendados = Producto.objects.filter(
        estado_producto="activo"
    ).select_related("categoria", "marca")[:8]

    # Obtener todas las marcas activas para mostrar en el carrusel
    marcas = Marca.objects.filter(activa=True)

    context = {
        "productos": productos_recomendados,
        "marcas": marcas,
    }
    return render(request, "ventas/index.html", context)


def producto(request, producto_id):
    # Vista para un producto específico
    producto = get_object_or_404(
        Producto, producto_id=producto_id, estado_producto="activo"
    )

    # Productos relacionados de la misma categoría
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria, estado_producto="activo"
    ).exclude(producto_id=producto_id)[:4]

    context = {
        "producto": producto,
        "productos_relacionados": productos_relacionados,
    }
    return render(request, "ventas/producto.html", context)


def catalogo(request):
    # Obtener todos los productos activos
    productos = Producto.objects.filter(estado_producto="activo").select_related(
        "categoria", "marca"
    )

    # Filtros opcionales
    categoria_slug = request.GET.get("categoria")
    marca_id = request.GET.get("marca")

    # Filtrar por slug de categoría
    if categoria_slug:
        categoria_obj = Categoria.objects.filter(
            slug=categoria_slug, activa=True
        ).first()
        if categoria_obj:
            productos = productos.filter(categoria=categoria_obj)

    if marca_id:
        productos = productos.filter(marca_id=marca_id)

    # Obtener todas las categorías y marcas para los filtros
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)

    context = {
        "productos": productos,
        "categorias": categorias,
        "marcas": marcas,
        "categoria_seleccionada": categoria_slug,
        "marca_seleccionada": marca_id,
    }
    return render(request, "ventas/catalogo.html", context)


def iniciosesion(request):
    if request.method == "POST":
        username = request.POST.get("username")  # Email o RUT
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(
                request,
                f"¡Bienvenido, {user.first_name}! Has iniciado sesión correctamente.",
            )
            return redirect("index")
        else:
            messages.error(request, "Usuario o Contraseña Incorrecta")

    return render(request, "ventas/iniciosesion.html")


def logout_view(request):
    # Vista para cerrar sesión"""
    login_aut(request)
    messages.success(request, "¡Has cerrado sesión exitosamente!")
    return redirect("index")


def registro_view(request):
    # Vista para registro de nuevos clientes"""
    if request.method == "POST":
        rut = request.POST.get("rut")
        nombres = request.POST.get("nombres")
        apellido_paterno = request.POST.get("apellido_paterno")
        apellido_materno = request.POST.get("apellido_materno")
        email = request.POST.get("email")
        telefono = request.POST.get("telefono")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        password = request.POST.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if ClientePersona.objects.filter(rut=rut).exists():
            messages.error(request, "Ya existe un cliente con este RUT.")
        elif ClientePersona.objects.filter(email=email).exists():
            messages.error(request, "Ya existe un cliente con este email.")
        else:
            try:
                # Crear nuevo cliente
                cliente = ClientePersona.objects.create(
                    rut=rut,
                    nombres=nombres,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    email=email,
                    telefono=telefono,
                    fecha_nacimiento=fecha_nacimiento,
                    estado=True,
                    password=password_hash,
                )

                try:
                    brevo_service = BrevoEmailService()
                    email_result = brevo_service.send_welcome_email(
                        cliente_email=email,
                        cliente_nombre=f"{nombres} {apellido_paterno}",
                    )

                    if email_result["success"]:
                        logger.info(f"Email de bienvenida enviado a {email}")
                        messages.success(
                            request,
                            "Cliente registrado exitosamente. Se ha enviado un correo de bienvenida. Ya puede iniciar sesión.",
                        )
                    else:
                        logger.warning(
                            f"No se pudo enviar email de bienvenida: {email_result['message']}"
                        )
                        messages.success(
                            request,
                            "Cliente registrado exitosamente. Ya puede iniciar sesión.",
                        )
                        messages.warning(
                            request, "No se pudo enviar el correo de bienvenida."
                        )

                except Exception as e:
                    logger.error(f"Error al enviar email de bienvenida: {e}")
                    messages.success(
                        request,
                        "Cliente registrado exitosamente. Ya puede iniciar sesión.",
                    )
                    messages.warning(
                        request, "No se pudo enviar el correo de bienvenida."
                    )
                return redirect("iniciosesion")

            except Exception as e:
                messages.error(request, f"Error al registrar cliente: {str(e)}")

    return render(request, "ventas/registro.html")

def olvide_contrasena(request):
    """Vista para solicitar recuperación de contraseña mediante RUT"""
    if request.method == "POST":
        rut = request.POST.get("rut", "").strip()
        
        # Formatear y validar RUT
        rut_formateado = formatear_rut(rut)
        
        if not validar_rut(rut_formateado):
            messages.error(request, "El RUT ingresado no es válido")
            return render(request, "ventas/olvide_contrasena.html", {"rut": rut})
        
        try:
            # Buscar cliente por RUT
            cliente = ClientePersona.objects.get(rut=rut_formateado, estado=True)
            
            # Generar token de recuperación
            token = cliente_token_generator.make_token(cliente)
            uid = urlsafe_base64_encode(force_bytes(cliente.cliente_persona_id))
            
            # Construir URL de restablecimiento
            reset_url = request.build_absolute_uri(
                reverse('restablecer_contrasena', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Enviar correo con Brevo
            email_service = BrevoEmailService()
            resultado = email_service.enviar_recuperacion_contrasena(
                email=cliente.email,
                nombre=cliente.nombres,
                reset_url=reset_url
            )
            
            if resultado['success']:
                messages.success(
                    request, 
                    f"Se ha enviado un correo a {cliente.email} con las instrucciones para restablecer tu contraseña."
                )
                return redirect('iniciosesion')
            else:
                messages.error(
                    request, 
                    f"Error al enviar el correo: {resultado['message']}"
                )
                
        except ClientePersona.DoesNotExist:
            # Por seguridad, no revelar si el RUT existe o no
            messages.success(
                request, 
                "Si el RUT está registrado, recibirás un correo con las instrucciones para restablecer tu contraseña."
            )
            return redirect('iniciosesion')
        except Exception as e:
            logger.error(f"Error en recuperación de contraseña: {str(e)}", exc_info=True)
            messages.error(request, "Ocurrió un error. Por favor, intenta nuevamente.")
    
    return render(request, "ventas/olvide_contrasena.html")


def restablecer_contrasena(request, uidb64, token):
    """Vista para restablecer la contraseña con el token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        cliente = ClientePersona.objects.get(cliente_persona_id=uid, estado=True)
    except (TypeError, ValueError, OverflowError, ClientePersona.DoesNotExist):
        cliente = None
    
    # Verificar token
    if cliente is None or not cliente_token_generator.check_token(cliente, token):
        messages.error(request, "El enlace de recuperación es inválido o ha expirado.")
        return redirect('iniciar_sesion')
    
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        
        # Validaciones
        if not password1 or not password2:
            messages.error(request, "Debes ingresar ambas contraseñas")
            return render(request, "ventas/restablecer_contrasena.html", {
                'uidb64': uidb64,
                'token': token
            })
        
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "ventas/restablecer_contrasena.html", {
                'uidb64': uidb64,
                'token': token
            })
        
        if len(password1) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres")
            return render(request, "ventas/restablecer_contrasena.html", {
                'uidb64': uidb64,
                'token': token
            })
        
        try:
            # Hash de la nueva contraseña
            password_hash = hashlib.sha256(password1.encode()).hexdigest()
            
            # Actualizar contraseña
            cliente.password = password_hash
            cliente.save()
            
            messages.success(request, "Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión.")
            return redirect('iniciosesion')
            
        except Exception as e:
            logger.error(f"Error al restablecer contraseña: {str(e)}", exc_info=True)
            messages.error(request, "Ocurrió un error al restablecer la contraseña.")
    
    return render(request, "ventas/restablecer_contrasena.html", {
        'uidb64': uidb64,
        'token': token,
        'cliente': cliente
    })
