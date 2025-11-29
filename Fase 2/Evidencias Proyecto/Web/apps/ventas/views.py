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
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from .brevo_service import BrevoEmailService
from .models import *

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

    # Filtro de búsqueda por texto
    search_query = request.GET.get("q", "").strip()
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains = search_query) |
            Q(descripcion__icontains = search_query) |
            Q(marca__nombre__icontains = search_query) |
            Q(categoria__nombre__icontains = search_query)
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
        "productos": productos.distinct(),  # distinct() para evitar duplicados en búsquedas
        "categorias": categorias,
        "marcas": marcas,
        "search_query": search_query,  # Para mostrar el término buscado
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

@login_required
def perfil_view(request):
    """Vista para ver el perfil del usuario"""
    try:
        # Obtener el cliente asociado al usuario logueado
        cliente = ClientePersona.objects.get(email=request.user.username)
        
        # Obtener historial de pedidos
        pedidos = Pedido.objects.filter(
            cliente_persona=cliente
        ).order_by('-fecha')[:10]  # Últimos 10 pedidos
        
        context = {
            'cliente': cliente,
            'pedidos': pedidos,
        }
        return render(request, "ventas/perfil.html", context)
    except ClientePersona.DoesNotExist:
        messages.error(request, "No se encontró información del perfil.")
        return redirect('index')


@login_required
def editar_perfil_view(request):
    """Vista para editar el perfil del usuario"""
    try:
        cliente = ClientePersona.objects.get(email=request.user.username)
        
        if request.method == "POST":
            # Actualizar datos del cliente
            cliente.nombres = request.POST.get("nombres", cliente.nombres)
            cliente.apellido_paterno = request.POST.get("apellido_paterno", cliente.apellido_paterno)
            cliente.apellido_materno = request.POST.get("apellido_materno", cliente.apellido_materno)
            cliente.telefono = request.POST.get("telefono", cliente.telefono)
            cliente.fecha_nacimiento = request.POST.get("fecha_nacimiento", cliente.fecha_nacimiento)
            
            # Actualizar email si cambió
            nuevo_email = request.POST.get("email")
            if nuevo_email and nuevo_email != cliente.email:
                # Verificar que el nuevo email no esté en uso
                if ClientePersona.objects.filter(email=nuevo_email).exclude(cliente_persona_id=cliente.cliente_persona_id).exists():
                    messages.error(request, "El email ya está en uso por otro usuario.")
                    return render(request, "ventas/editar_perfil.html", {'cliente': cliente})
                
                cliente.email = nuevo_email
                # Actualizar también el username del User
                user = request.user
                user.username = nuevo_email
                user.email = nuevo_email
                user.save()
            
            cliente.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('perfil')
        
        context = {'cliente': cliente}
        return render(request, "ventas/editar_perfil.html", context)
        
    except ClientePersona.DoesNotExist:
        messages.error(request, "No se encontró información del perfil.")
        return redirect('index')


@login_required
def cambiar_contrasena_view(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == "POST":
        password_actual = request.POST.get("password_actual")
        password_nueva = request.POST.get("password_nueva")
        password_confirmacion = request.POST.get("password_confirmar")
        if password_nueva != password_confirmacion:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
            return render(request, "ventas/cambiar_contrasena.html")
        
        try:
            cliente = ClientePersona.objects.get(email=request.user.username)
            
            # Verificar contraseña actual
            password_actual_hash = hashlib.sha256(password_actual.encode()).hexdigest()
            if password_actual_hash != cliente.password:
                messages.error(request, "La contraseña actual es incorrecta.")
                return render(request, "ventas/cambiar_contrasena.html")
            
            # Verificar que las nuevas contraseñas coincidan

            
            # Actualizar contraseña
            password_nueva_hash = hashlib.sha256(password_nueva.encode()).hexdigest()
            cliente.password = password_nueva_hash
            cliente.save()
            
            # Actualizar también la contraseña del User de Django
            user = request.user
            user.set_password(password_nueva)
            user.save()
            
            # Re-autenticar al usuario
            user = authenticate(request, username=user.username, password=password_nueva)
            if user:
                login(request, user)
            
            messages.success(request, "Contraseña cambiada exitosamente.")
            return redirect('perfil')
            
        except ClientePersona.DoesNotExist:
            messages.error(request, "No se encontró información del perfil.")
            return redirect('index')
    
    return render(request, "ventas/cambiar_contrasena.html")


def olvide_contrasena(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            cliente = ClientePersona.objects.get(email=email)
            user = User.objects.get(username=email)
            
            # Generar token para recuperación
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Crear URL de recuperación
            reset_url = request.build_absolute_uri(
                f"/restablecer-contrasena/{uid}/{token}/"
            )
            
            try:
                # Enviar email con Brevo
                brevo_service = BrevoEmailService()
                email_result = brevo_service.send_password_reset_email(
                    cliente_email=email,
                    cliente_nombre=f"{cliente.nombres} {cliente.apellido_paterno}",
                    reset_url=reset_url
                )
                
                if email_result["success"]:
                    messages.success(
                        request,
                        "Se ha enviado un correo con instrucciones para restablecer tu contraseña."
                    )
                else:
                    messages.warning(
                        request,
                        "No se pudo enviar el correo. Por favor, contacta con soporte."
                    )
            except Exception as e:
                logger.error(f"Error al enviar email de recuperación: {e}")
                messages.warning(
                    request,
                    "No se pudo enviar el correo. Por favor, contacta con soporte."
                )
            
            return redirect('iniciosesion')
            
        except (ClientePersona.DoesNotExist, User.DoesNotExist):
            messages.error(request, "No existe un usuario con ese correo electrónico.")
    
    return render(request, "ventas/olvide_contrasena.html")


def restablecer_contrasena(request, uidb64, token):
    """Vista para restablecer la contraseña con token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password_nueva = request.POST.get("password_nueva")
            password_confirmacion = request.POST.get("password_confirmacion")
            
            if password_nueva != password_confirmacion:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, "ventas/restablecer_contrasena.html")
            
            try:
                # Actualizar contraseña del cliente
                cliente = ClientePersona.objects.get(email=user.username)
                password_nueva_hash = hashlib.sha256(password_nueva.encode()).hexdigest()
                cliente.password = password_nueva_hash
                cliente.save()
                
                # Actualizar contraseña del User de Django
                user.set_password(password_nueva)
                user.save()
                
                messages.success(request, "Contraseña restablecida exitosamente. Ya puedes iniciar sesión.")
                return redirect('iniciosesion')
                
            except ClientePersona.DoesNotExist:
                messages.error(request, "Error al restablecer la contraseña.")
                return redirect('iniciosesion')
        
        return render(request, "ventas/restablecer_contrasena.html")
    else:
        messages.error(request, "El enlace de recuperación es inválido o ha expirado.")
        return redirect('olvide_contrasena')


