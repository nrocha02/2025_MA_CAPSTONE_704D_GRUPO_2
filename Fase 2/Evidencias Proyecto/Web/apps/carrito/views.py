from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .carrito import Carrito
from .models import CheckoutSession
from .shipping_service import calcular_costo_envio, obtener_opciones_envio
from apps.ventas.models import Producto, Pedido, PedidoItem, Pago, SesionInvitado
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
import uuid
import json
import logging
import re
import http.client
import os

logger = logging.getLogger(__name__)


def obtener_regiones():
    """Obtiene las regiones desde la API de RapidAPI"""
    try:
        conn = http.client.HTTPSConnection("multicourier.p.rapidapi.com")

        headers = {
            "x-rapidapi-key": os.getenv("X_RAPIDAPI_KEY", ""),
            "x-rapidapi-host": "multicourier.p.rapidapi.com",
        }

        conn.request("GET", "/location/state", headers=headers)
        res = conn.getresponse()
        data = res.read()

        regiones = json.loads(data.decode("utf-8"))
        return regiones
    except Exception as e:
        logger.error(f"Error al obtener regiones: {str(e)}")
        return []


def obtener_comunas(codigo_region):
    """Obtiene las comunas de una región desde la API de RapidAPI"""
    try:
        conn = http.client.HTTPSConnection("multicourier.p.rapidapi.com")

        headers = {
            "x-rapidapi-key": os.getenv("X_RAPIDAPI_KEY", ""),
            "x-rapidapi-host": "multicourier.p.rapidapi.com",
        }

        conn.request("GET", f"/location/district/{codigo_region}", headers=headers)
        res = conn.getresponse()
        data = res.read()

        resultado = json.loads(data.decode("utf-8"))
        return resultado.get("locations", [])
    except Exception as e:
        logger.error(f"Error al obtener comunas: {str(e)}")
        return []


def validar_rut(rut):
    """Valida formato y dígito verificador del RUT chileno"""
    # Eliminar puntos y guión
    rut_limpio = rut.replace(".", "").replace("-", "").upper()

    # Verificar formato básico (7-8 dígitos + dígito verificador)
    if not re.match(r"^\d{7,8}[0-9K]$", rut_limpio):
        return False

    # Separar cuerpo y dígito verificador
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]

    # Calcular dígito verificador
    suma = 0
    multiplo = 2

    for i in range(len(cuerpo) - 1, -1, -1):
        suma += int(cuerpo[i]) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2

    dv_esperado = 11 - (suma % 11)
    dv_calculado = (
        "K" if dv_esperado == 10 else ("0" if dv_esperado == 11 else str(dv_esperado))
    )

    return dv == dv_calculado


def validar_telefono(telefono):
    """Valida formato de teléfono chileno (9 dígitos)"""
    # Eliminar espacios y caracteres especiales
    telefono_limpio = re.sub(r"[^\d]", "", telefono)

    # Debe tener exactamente 9 dígitos
    return len(telefono_limpio) == 9 and telefono_limpio.isdigit()


def formatear_rut(rut):
    """Formatea el RUT al formato XXXXXXXX-X"""
    rut_limpio = rut.replace(".", "").replace("-", "").upper()
    if len(rut_limpio) < 2:
        return rut
    return f"{rut_limpio[:-1]}-{rut_limpio[-1]}"


def get_webpay_options():
    """Obtiene las opciones de configuración para Webpay"""
    return WebpayOptions(
        commerce_code=settings.TRANSBANK_COMMERCE_CODE,
        api_key=settings.TRANSBANK_API_KEY,
        integration_type=IntegrationType.TEST
        if settings.TRANSBANK_ENVIRONMENT == "TEST"
        else IntegrationType.LIVE,
    )


def ver_carrito(request):
    carrito = Carrito(request)
    productos_carrito = carrito.get_productos()
    subtotal = carrito.get_subtotal()
    # El costo de envío se calculará dinámicamente en el checkout
    costo_envio = 0
    total = subtotal + costo_envio

    context = {
        "productos_carrito": productos_carrito,
        "subtotal": subtotal,
        "costo_envio": costo_envio,
        "total": total,
        "carrito_vacio": len(productos_carrito) == 0,
    }
    return render(request, "carrito/ver_carrito.html", context)


def agregar_carrito(request):
    carrito = Carrito(request)
    if request.POST.get("action") == "post":
        producto_id = int(request.POST.get("producto_id"))
        cantidad = int(request.POST.get("cantidad", 1))
        producto = get_object_or_404(Producto, producto_id=producto_id)
        carrito.agregar(producto=producto, cantidad=cantidad)
        return JsonResponse(
            {
                "success": True,
                "nombre_producto": producto.nombre,
                "total_productos": carrito.get_total_productos(),
            }
        )


def eliminar_carrito(request):
    carrito = Carrito(request)
    if request.POST.get("action") == "post":
        producto_id = request.POST.get("producto_id")
        carrito.eliminar(producto_id)
        return JsonResponse(
            {
                "success": True,
                "total_productos": carrito.get_total_productos(),
                "subtotal": carrito.get_subtotal(),
                "total": carrito.get_total(),
            }
        )


def actualizar_carrito(request):
    carrito = Carrito(request)
    if request.POST.get("action") == "post":
        producto_id = request.POST.get("producto_id")
        cantidad = int(request.POST.get("cantidad"))
        carrito.actualizar_cantidad(producto_id, cantidad)
        return JsonResponse(
            {
                "success": True,
                "total_productos": carrito.get_total_productos(),
                "subtotal": carrito.get_subtotal(),
                "total": carrito.get_total(),
            }
        )


def checkout(request):
    """Vista para mostrar el formulario de checkout"""
    carrito = Carrito(request)
    productos_carrito = carrito.get_productos()

    if len(productos_carrito) == 0:
        return redirect("carrito:ver_carrito")

    subtotal = carrito.get_subtotal()
    # El costo de envío se calculará cuando se seleccione la comuna
    costo_envio = 0
    total = subtotal

    # Obtener regiones desde la API
    regiones = obtener_regiones()

    context = {
        "productos_carrito": productos_carrito,
        "subtotal": subtotal,
        "costo_envio": costo_envio,
        "total": total,
        "regiones": regiones,
    }

    return render(request, "carrito/checkout.html", context)


def obtener_comunas_ajax(request):
    """Vista AJAX para obtener comunas de una región"""
    codigo_region = request.GET.get("codigo_region", "")

    if not codigo_region:
        return JsonResponse({"error": "Código de región no proporcionado"}, status=400)

    comunas = obtener_comunas(codigo_region)
    return JsonResponse({"comunas": comunas})


def calcular_costo_envio_ajax(request):
    """Vista AJAX para calcular el costo de envío según la comuna"""
    ciudad = request.GET.get("ciudad", "")

    if not ciudad:
        return JsonResponse({"error": "Ciudad no proporcionada"}, status=400)

    try:
        carrito = Carrito(request)
        items_carrito = carrito.get_productos()

        # Calcular costo de envío
        costo_envio_valor = calcular_costo_envio(ciudad, items_carrito)

        # Obtener opciones de envío disponibles
        opciones = obtener_opciones_envio(ciudad, items_carrito)

        return JsonResponse({"costo_envio": costo_envio_valor, "opciones": opciones})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def iniciar_pago(request):
    """Vista para iniciar el pago con Transbank"""
    if request.method != "POST":
        return redirect("carrito:checkout")

    try:
        carrito = Carrito(request)
        productos_carrito = carrito.get_productos()

        if len(productos_carrito) == 0:
            return redirect("carrito:ver_carrito")

        # Obtener datos del formulario
        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        email = request.POST.get("email")
        telefono = request.POST.get("telefono")
        rut = request.POST.get("rut", "")
        calle = request.POST.get("calle")
        ciudad = request.POST.get("ciudad")
        region = request.POST.get("region")
        codigo_postal = request.POST.get("codigo_postal", "")

        # Validar datos básicos (sin código postal que ahora es opcional)
        if not all([nombres, apellidos, email, telefono, rut, calle, ciudad, region]):
            # Calcular costo de envío dinámicamente
            costo_envio_calculado = calcular_costo_envio(
                ciudad if ciudad else "", productos_carrito
            )

            return render(
                request,
                "carrito/checkout.html",
                {
                    "error": "Por favor completa todos los campos obligatorios",
                    "productos_carrito": productos_carrito,
                    "subtotal": carrito.get_subtotal(),
                    "costo_envio": costo_envio_calculado,
                    "total": carrito.get_subtotal() + costo_envio_calculado,
                    "regiones": obtener_regiones(),
                },
            )

        # Validar formato de RUT
        if not validar_rut(rut):
            # Calcular costo de envío dinámicamente
            costo_envio_calculado = calcular_costo_envio(ciudad, productos_carrito)

            return render(
                request,
                "carrito/checkout.html",
                {
                    "error": "El RUT ingresado no es válido. Formato esperado: XXXXXXXX-X",
                    "productos_carrito": productos_carrito,
                    "subtotal": carrito.get_subtotal(),
                    "costo_envio": costo_envio_calculado,
                    "total": carrito.get_subtotal() + costo_envio_calculado,
                    "regiones": obtener_regiones(),
                },
            )

        # Validar formato de teléfono
        if not validar_telefono(telefono):
            # Calcular costo de envío dinámicamente
            costo_envio_calculado = calcular_costo_envio(ciudad, productos_carrito)

            return render(
                request,
                "carrito/checkout.html",
                {
                    "error": "El teléfono debe tener exactamente 9 dígitos (ej: 912345678)",
                    "productos_carrito": productos_carrito,
                    "subtotal": carrito.get_subtotal(),
                    "costo_envio": costo_envio_calculado,
                    "total": carrito.get_subtotal() + costo_envio_calculado,
                    "regiones": obtener_regiones(),
                },
            )

        # Formatear RUT y teléfono
        rut_formateado = formatear_rut(rut)
        telefono_limpio = re.sub(r"[^\d]", "", telefono)

        # Crear sesión única
        session_id = str(uuid.uuid4())

        # Guardar datos del carrito
        carrito_data = {}
        for producto in productos_carrito:
            carrito_data[str(producto.producto_id)] = {
                "nombre": producto.nombre,
                "precio": producto.precio,
                "cantidad": producto.cantidad_carrito,
                "subtotal": producto.subtotal,
            }

        # Calcular costo de envío dinámicamente
        costo_envio_calculado = calcular_costo_envio(ciudad, productos_carrito)
        total_con_envio = carrito.get_subtotal() + costo_envio_calculado

        # Crear checkout session
        checkout_session = CheckoutSession.objects.create(
            session_id=session_id,
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            telefono=telefono_limpio,
            rut=rut_formateado,
            calle=calle,
            ciudad=ciudad,
            region=region,
            codigo_postal=codigo_postal if codigo_postal else None,
            total=total_con_envio,
            subtotal=carrito.get_subtotal(),
            costo_envio=costo_envio_calculado,
            carrito_data=carrito_data,
            estado="pendiente",
        )

        # Crear transacción en Transbank
        buy_order = f"ORDER-{checkout_session.pk}"
        session_id_tb = session_id
        amount = checkout_session.total
        return_url = request.build_absolute_uri(reverse("carrito:confirmar_pago"))

        logger.info(
            f"Iniciando transacción Transbank: buy_order={buy_order}, amount={amount}"
        )

        # El SDK de Transbank usa las credenciales de prueba por defecto
        # Para producción, se debe configurar con las credenciales reales
        tx = Transaction(get_webpay_options())
        response = tx.create(buy_order, session_id_tb, amount, return_url)

        # Guardar token y URL de Transbank
        checkout_session.transbank_token = response["token"]
        checkout_session.transbank_url = response["url"]
        checkout_session.save()

        logger.info(f"Transacción creada exitosamente: token={response['token']}")

        # Redirigir a Transbank
        return redirect(f"{response['url']}?token_ws={response['token']}")

    except Exception as e:
        logger.error(f"Error al iniciar pago: {str(e)}", exc_info=True)
        # Calcular costo de envío dinámicamente
        costo_envio_calculado = calcular_costo_envio(
            ciudad if ciudad else "", productos_carrito
        )

        return render(
            request,
            "carrito/checkout.html",
            {
                "error": f"Error al procesar el pago: {str(e)}",
                "productos_carrito": productos_carrito,
                "subtotal": carrito.get_subtotal(),
                "costo_envio": costo_envio_calculado,
                "total": carrito.get_subtotal() + costo_envio_calculado,
            },
        )


def confirmar_pago(request):
    """Vista para confirmar el pago después del retorno de Transbank"""
    token = request.GET.get("token_ws") or request.POST.get("token_ws")

    if not token:
        return render(
            request, "carrito/pago_error.html", {"error": "Token de pago no encontrado"}
        )

    try:
        # Crear instancia de Transaction con las opciones configuradas
        tx = Transaction(get_webpay_options())

        # Confirmar transacción
        logger.info(f"Confirmando transacción con token: {token}")
        response = tx.commit(token)

        logger.info(f"Respuesta de Transbank: {response}")

        # Buscar checkout session
        checkout_session = get_object_or_404(CheckoutSession, transbank_token=token)

        # Verificar si el pago fue exitoso
        if response["status"] == "AUTHORIZED" and response["response_code"] == 0:
            # Marcar sesión como pagada
            checkout_session.estado = "pagado"
            checkout_session.save()

            # Determinar el tipo de cliente
            cliente_invitado_id = None

            # Si no hay cliente autenticado, crear o recuperar sesión de invitado por email
            if (
                not checkout_session.cliente_persona_id
                and not checkout_session.cliente_empresa_id
            ):
                sesion_invitado, created = SesionInvitado.objects.get_or_create(
                    email=checkout_session.email[:50],  # Limitar a 50 caracteres
                    defaults={"estado": "activa"},
                )
                cliente_invitado_id = sesion_invitado.cliente_invitado_id

            # Crear pedido en la base de datos
            pedido = Pedido.objects.create(
                calle=checkout_session.calle,
                ciudad=checkout_session.ciudad,
                region=checkout_session.region,
                codigo_postal=checkout_session.codigo_postal,
                total=checkout_session.total,
                precio_envio=checkout_session.costo_envio,
                estado="Procesando",
                cliente_persona_id=checkout_session.cliente_persona_id,
                cliente_empresa_id=checkout_session.cliente_empresa_id,
                cliente_invitado_id=cliente_invitado_id,
            )

            # Crear items del pedido
            for producto_id, item_data in checkout_session.carrito_data.items():
                producto = Producto.objects.get(producto_id=int(producto_id))
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item_data["cantidad"],
                    precio_unitario=item_data["precio"],
                    subtotal=item_data["subtotal"],
                )

                # Actualizar stock
                producto.stock -= item_data["cantidad"]
                producto.save()

            # Crear el registro de pago
            Pago.objects.create(
                pedido=pedido,
                monto=checkout_session.total,
                metodo="Webpay Plus",
                estado="pagado",  # ← Cambiado de 'aprobado' a 'pagado'
                transbank_token=token,
            )

            # Limpiar carrito
            carrito = Carrito(request)
            carrito.limpiar()

            # Redirigir a página de éxito
            return render(
                request,
                "carrito/pago_exitoso.html",
                {
                    "pedido": pedido,
                    "checkout_session": checkout_session,
                    "transbank_response": response,
                },
            )
        else:
            # Pago rechazado
            checkout_session.estado = "error"
            checkout_session.save()

            return render(
                request,
                "carrito/pago_error.html",
                {
                    "error": "El pago fue rechazado",
                    "response_code": response.get("response_code"),
                    "status": response.get("status"),
                },
            )

    except Exception as e:
        logger.error(f"Error al confirmar pago: {str(e)}", exc_info=True)
        return render(
            request,
            "carrito/pago_error.html",
            {"error": f"Error al confirmar el pago: {str(e)}"},
        )
