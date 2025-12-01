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
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt

from ..ventas.utils import formatear_rut, validar_rut
from .brevo_service import BrevoEmailService
from .forms import (
    CambiarContrasenaForm,
    ClientePerfilForm,
    DireccionForm,
    MetodoPagoForm,
)
from .models import *
from .tokens import cliente_token_generator

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

            # Guardar cliente_id en la sesión
            try:
                cliente = ClientePersona.objects.get(email=username)
                request.session["cliente_id"] = cliente.cliente_persona_id
            except ClientePersona.DoesNotExist:
                pass

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
                reverse(
                    "restablecer_contrasena", kwargs={"uidb64": uid, "token": token}
                )
            )

            # Enviar correo con Brevo
            email_service = BrevoEmailService()
            resultado = email_service.enviar_recuperacion_contrasena(
                email=cliente.email, nombre=cliente.nombres, reset_url=reset_url
            )

            if resultado["success"]:
                messages.success(
                    request,
                    f"Se ha enviado un correo a {cliente.email} con las instrucciones para restablecer tu contraseña.",
                )
                return redirect("iniciosesion")
            else:
                messages.error(
                    request, f"Error al enviar el correo: {resultado['message']}"
                )

        except ClientePersona.DoesNotExist:
            # Por seguridad, no revelar si el RUT existe o no
            messages.success(
                request,
                "Si el RUT está registrado, recibirás un correo con las instrucciones para restablecer tu contraseña.",
            )
            return redirect("iniciosesion")
        except Exception as e:
            logger.error(
                f"Error en recuperación de contraseña: {str(e)}", exc_info=True
            )
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
        return redirect("iniciar_sesion")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validaciones
        if not password1 or not password2:
            messages.error(request, "Debes ingresar ambas contraseñas")
            return render(
                request,
                "ventas/restablecer_contrasena.html",
                {"uidb64": uidb64, "token": token},
            )

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(
                request,
                "ventas/restablecer_contrasena.html",
                {"uidb64": uidb64, "token": token},
            )

        if len(password1) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres")
            return render(
                request,
                "ventas/restablecer_contrasena.html",
                {"uidb64": uidb64, "token": token},
            )

        try:
            # Hash de la nueva contraseña
            password_hash = hashlib.sha256(password1.encode()).hexdigest()

            # Actualizar contraseña
            cliente.password = password_hash
            cliente.save()

            messages.success(
                request,
                "Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión.",
            )
            return redirect("iniciosesion")

        except Exception as e:
            logger.error(f"Error al restablecer contraseña: {str(e)}", exc_info=True)
            messages.error(request, "Ocurrió un error al restablecer la contraseña.")

    return render(
        request,
        "ventas/restablecer_contrasena.html",
        {"uidb64": uidb64, "token": token, "cliente": cliente},
    )


@login_required
def mi_perfil(request):
    """Vista principal del perfil del cliente"""
    try:
        # Obtener el cliente actual desde la sesión
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión para acceder a tu perfil.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        # Obtener direcciones del cliente
        direcciones = Direccion.objects.filter(cliente_persona=cliente).order_by(
            "-direccion_id"
        )

        # Obtener métodos de pago activos del cliente
        metodos_pago = MetodoPago.objects.filter(
            cliente_persona=cliente, estado="activo"
        ).order_by("-fecha_creacion")

        context = {
            "cliente": cliente,
            "direcciones": direcciones,
            "metodos_pago": metodos_pago,
        }

        return render(request, "ventas/perfil/mi_perfil.html", context)

    except Exception as e:
        logger.error(f"Error en mi_perfil: {str(e)}", exc_info=True)
        messages.error(request, "Error al cargar el perfil.")
        return redirect("index")


@login_required
def editar_perfil(request):
    """Vista para editar información personal del cliente"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        if request.method == "POST":
            form = ClientePerfilForm(request.POST, instance=cliente)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Tu información personal ha sido actualizada exitosamente."
                )
                return redirect("mi_perfil")
        else:
            form = ClientePerfilForm(instance=cliente)

        context = {
            "form": form,
            "cliente": cliente,
        }

        return render(request, "ventas/perfil/editar_perfil.html", context)

    except Exception as e:
        logger.error(f"Error en editar_perfil: {str(e)}", exc_info=True)
        messages.error(request, "Error al editar el perfil.")
        return redirect("mi_perfil")


@login_required
def cambiar_contrasena(request):
    """Vista para cambiar la contraseña del cliente"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        if request.method == "POST":
            form = CambiarContrasenaForm(request.POST, cliente=cliente)
            if form.is_valid():
                # Hash de la nueva contraseña
                nueva_contrasena = form.cleaned_data["contrasena_nueva"]
                password_hash = hashlib.sha256(nueva_contrasena.encode()).hexdigest()

                # Actualizar contraseña
                cliente.password = password_hash
                cliente.save()

                messages.success(
                    request, "Tu contraseña ha sido cambiada exitosamente."
                )
                return redirect("mi_perfil")
        else:
            form = CambiarContrasenaForm(cliente=cliente)

        context = {
            "form": form,
            "cliente": cliente,
        }

        return render(request, "ventas/perfil/cambiar_contrasena.html", context)

    except Exception as e:
        logger.error(f"Error en cambiar_contrasena: {str(e)}", exc_info=True)
        messages.error(request, "Error al cambiar la contraseña.")
        return redirect("mi_perfil")


@login_required
def agregar_direccion(request):
    """Vista para agregar una nueva dirección"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        if request.method == "POST":
            form = DireccionForm(request.POST)
            if form.is_valid():
                direccion = form.save(commit=False)
                direccion.cliente_persona = cliente
                direccion.save()
                messages.success(request, "Dirección agregada exitosamente.")
                return redirect("mi_perfil")
        else:
            form = DireccionForm()

        context = {
            "form": form,
            "cliente": cliente,
            "accion": "Agregar",
        }

        return render(request, "ventas/perfil/form_direccion.html", context)

    except Exception as e:
        logger.error(f"Error en agregar_direccion: {str(e)}", exc_info=True)
        messages.error(request, "Error al agregar la dirección.")
        return redirect("mi_perfil")


@login_required
def editar_direccion(request, direccion_id):
    """Vista para editar una dirección existente"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)
        direccion = get_object_or_404(
            Direccion, direccion_id=direccion_id, cliente_persona=cliente
        )

        if request.method == "POST":
            form = DireccionForm(request.POST, instance=direccion)
            if form.is_valid():
                form.save()
                messages.success(request, "Dirección actualizada exitosamente.")
                return redirect("mi_perfil")
        else:
            form = DireccionForm(instance=direccion)

        context = {
            "form": form,
            "cliente": cliente,
            "direccion": direccion,
            "accion": "Editar",
        }

        return render(request, "ventas/perfil/form_direccion.html", context)

    except Exception as e:
        logger.error(f"Error en editar_direccion: {str(e)}", exc_info=True)
        messages.error(request, "Error al editar la dirección.")
        return redirect("mi_perfil")


@login_required
def eliminar_direccion(request, direccion_id):
    """Vista para eliminar una dirección"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)
        direccion = get_object_or_404(
            Direccion, direccion_id=direccion_id, cliente_persona=cliente
        )

        if request.method == "POST":
            direccion.delete()
            messages.success(request, "Dirección eliminada exitosamente.")
            return redirect("mi_perfil")

        context = {
            "direccion": direccion,
            "cliente": cliente,
        }

        return render(
            request, "ventas/perfil/confirmar_eliminar_direccion.html", context
        )

    except Exception as e:
        logger.error(f"Error en eliminar_direccion: {str(e)}", exc_info=True)
        messages.error(request, "Error al eliminar la dirección.")
        return redirect("mi_perfil")


@login_required
def agregar_metodo_pago(request):
    """Vista para agregar un nuevo método de pago"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        if request.method == "POST":
            form = MetodoPagoForm(request.POST)
            if form.is_valid():
                metodo_pago = form.save(commit=False)
                metodo_pago.cliente_persona = cliente
                metodo_pago.save()
                messages.success(request, "Método de pago agregado exitosamente.")
                return redirect("mi_perfil")
        else:
            form = MetodoPagoForm()

        context = {
            "form": form,
            "cliente": cliente,
            "accion": "Agregar",
        }

        return render(request, "ventas/perfil/form_metodo_pago.html", context)

    except Exception as e:
        logger.error(f"Error en agregar_metodo_pago: {str(e)}", exc_info=True)
        messages.error(request, "Error al agregar el método de pago.")
        return redirect("mi_perfil")


@login_required
def editar_metodo_pago(request, metodo_pago_id):
    """Vista para editar un método de pago existente"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)
        metodo_pago = get_object_or_404(
            MetodoPago, metodo_pago_id=metodo_pago_id, cliente_persona=cliente
        )

        if request.method == "POST":
            form = MetodoPagoForm(request.POST, instance=metodo_pago)
            if form.is_valid():
                form.save()
                messages.success(request, "Método de pago actualizado exitosamente.")
                return redirect("mi_perfil")
        else:
            # Para edición, pre-cargar datos pero no mostrar número completo de tarjeta
            form = MetodoPagoForm(instance=metodo_pago)
            # Limpiar el campo número de tarjeta por seguridad
            form.fields["numero_tarjeta"].required = False
            form.fields["cvv"].required = False

        context = {
            "form": form,
            "cliente": cliente,
            "metodo_pago": metodo_pago,
            "accion": "Editar",
        }

        return render(request, "ventas/perfil/form_metodo_pago.html", context)

    except Exception as e:
        logger.error(f"Error en editar_metodo_pago: {str(e)}", exc_info=True)
        messages.error(request, "Error al editar el método de pago.")
        return redirect("mi_perfil")


@login_required
def eliminar_metodo_pago(request, metodo_pago_id):
    """Vista para eliminar (desactivar) un método de pago"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)
        metodo_pago = get_object_or_404(
            MetodoPago, metodo_pago_id=metodo_pago_id, cliente_persona=cliente
        )

        if request.method == "POST":
            # Desactivar en lugar de eliminar
            metodo_pago.estado = "inactivo"
            metodo_pago.save()
            messages.success(request, "Método de pago eliminado exitosamente.")
            return redirect("mi_perfil")

        context = {
            "metodo_pago": metodo_pago,
            "cliente": cliente,
        }

        return render(
            request, "ventas/perfil/confirmar_eliminar_metodo_pago.html", context
        )

    except Exception as e:
        logger.error(f"Error en eliminar_metodo_pago: {str(e)}", exc_info=True)
        messages.error(request, "Error al eliminar el método de pago.")
        return redirect("mi_perfil")


@login_required
def mis_pedidos(request):
    """Vista para listar todos los pedidos del cliente"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión para ver tus pedidos.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        # Obtener todos los pedidos del cliente ordenados por fecha descendente
        pedidos = (
            Pedido.objects.filter(cliente_persona=cliente)
            .select_related("cliente_persona")
            .prefetch_related("items__producto")
            .order_by("-fecha")
        )

        # Paginación (10 pedidos por página)
        paginator = Paginator(pedidos, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Calcular estadísticas
        total_pedidos = pedidos.count()
        pedidos_pendientes = pedidos.filter(estado="Pendiente de pago").count()
        pedidos_completados = pedidos.filter(estado="Entregado").count()

        context = {
            "cliente": cliente,
            "page_obj": page_obj,
            "total_pedidos": total_pedidos,
            "pedidos_pendientes": pedidos_pendientes,
            "pedidos_completados": pedidos_completados,
        }

        return render(request, "ventas/perfil/mis_pedidos.html", context)

    except Exception as e:
        logger.error(f"Error en mis_pedidos: {str(e)}", exc_info=True)
        messages.error(request, "Error al cargar los pedidos.")
        return redirect("mi_perfil")


@login_required
def detalle_pedido(request, pedido_id):
    """Vista para ver el detalle de un pedido específico"""
    try:
        cliente_id = request.session.get("cliente_id")
        if not cliente_id:
            messages.error(request, "Debes iniciar sesión.")
            return redirect("iniciosesion")

        cliente = get_object_or_404(ClientePersona, cliente_persona_id=cliente_id)

        # Obtener el pedido asegurando que pertenece al cliente
        pedido = get_object_or_404(
            Pedido.objects.select_related("cliente_persona").prefetch_related(
                "items__producto__marca", "items__producto__categoria"
            ),
            pedido_id=pedido_id,
            cliente_persona=cliente,
        )

        # Obtener todos los items del pedido
        items = pedido.items.all()

        # Calcular subtotal sin envío
        subtotal = sum(item.subtotal for item in items)

        context = {
            "cliente": cliente,
            "pedido": pedido,
            "items": items,
            "subtotal": subtotal,
        }

        return render(request, "ventas/perfil/detalle_pedido.html", context)

    except Exception as e:
        logger.error(f"Error en detalle_pedido: {str(e)}", exc_info=True)
        messages.error(request, "Error al cargar el detalle del pedido.")
        return redirect("mis_pedidos")
