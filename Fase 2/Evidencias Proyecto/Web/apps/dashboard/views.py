import json
import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import (
    Avg,
    Case,
    Count,
    DecimalField,
    F,
    FloatField,
    IntegerField,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import (
    Coalesce,
    Extract,
    TruncDate,
    TruncMonth,
    TruncWeek,
)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from apps.ventas.models import (
    Categoria,
    ClienteEmpresa,
    ClientePersona,
    DocumentoTributario,
    Marca,
    MovimientoStock,
    Pago,
    Pedido,
    PedidoItem,
    Producto,
)

from .models import CostoEnvioComuna
from .storage import delete_product_image, is_spaces_configured, upload_product_image

# Configurar logger
logger = logging.getLogger(__name__)


def admin_dashboard(request):
    """Dashboard principal de administración con métricas de ventas y productos"""
    # Métricas de productos
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(estado_producto="activo").count()
    total_categorias = Categoria.objects.count()
    categorias_activas = Categoria.objects.filter(activa=True).count()
    total_marcas = Marca.objects.count()
    marcas_activas = Marca.objects.filter(activa=True).count()

    # Métricas de ventas
    today = timezone.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())

    # Ventas del mes actual
    ventas_mes = Pedido.objects.filter(
        fecha__gte=month_start, estado__in=["Procesando"]
    ).aggregate(total_ventas=Coalesce(Sum("total"), 0), num_pedidos=Count("pedido_id"))

    # Ventas de la semana
    ventas_semana = Pedido.objects.filter(
        fecha__gte=week_start, estado__in=["Procesando"]
    ).aggregate(total_ventas=Coalesce(Sum("total"), 0), num_pedidos=Count("pedido_id"))

    # Ventas del día
    ventas_hoy = Pedido.objects.filter(
        fecha__date=today, estado__in=["Procesando"]
    ).aggregate(total_ventas=Coalesce(Sum("total"), 0), num_pedidos=Count("pedido_id"))

    # Productos con stock bajo (menos de 10)
    productos_stock_bajo = Producto.objects.filter(
        stock__lt=10, estado_producto="activo"
    ).count()

    # Top 5 productos más vendidos (este mes)
    productos_top = (
        PedidoItem.objects.filter(
            pedido__fecha__gte=month_start, pedido__estado__in=["Procesando"]
        )
        .values("producto__nombre", "producto__sku")
        .annotate(
            total_vendido=Sum("cantidad"),
            ingresos=Sum(F("cantidad") * F("precio_unitario")),
        )
        .order_by("-total_vendido")[:5]
    )

    # Últimos pedidos
    ultimos_pedidos = Pedido.objects.select_related(
        "cliente_persona", "cliente_empresa"
    ).order_by("-fecha")[:10]

    context = {
        "total_productos": total_productos,
        "productos_activos": productos_activos,
        "total_categorias": total_categorias,
        "categorias_activas": categorias_activas,
        "total_marcas": total_marcas,
        "marcas_activas": marcas_activas,
        "productos_stock_bajo": productos_stock_bajo,
        "ventas_mes": ventas_mes,
        "ventas_semana": ventas_semana,
        "ventas_hoy": ventas_hoy,
        "productos_top": productos_top,
        "ultimos_pedidos": ultimos_pedidos,
    }
    return render(request, "dashboard/admin/dashboard.html", context)


# CRUD CATEGORÍAS


def categoria_list(request):
    """Lista todas las categorías"""
    from django.db.models import Count

    categorias = Categoria.objects.annotate(productos_count=Count("producto")).order_by(
        "nivel", "nombre"
    )

    # Paginación
    paginator = Paginator(categorias, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"categorias": page_obj, "titulo": "Gestión de Categorías"}
    return render(request, "dashboard/categoria/list.html", context)


def categoria_create(request):
    """Crear nueva categoría"""
    if request.method == "POST":
        try:
            nombre = request.POST.get("nombre")
            descripcion = request.POST.get("descripcion", "")
            categoria_padre_id = request.POST.get("categoria_padre")

            # Determinar el nivel
            nivel = 1
            categoria_padre = None
            if categoria_padre_id:
                categoria_padre = Categoria.objects.get(categoria_id=categoria_padre_id)
                nivel = categoria_padre.nivel + 1

            categoria = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                categoria_padre=categoria_padre,
                nivel=nivel,
                slug=slugify(nombre),
                activa=True,
            )

            messages.success(request, f'Categoría "{nombre}" creada exitosamente.')
            return redirect("dashboard:categoria_list")

        except Exception as e:
            messages.error(request, f"Error al crear categoría: {str(e)}")

    # Obtener categorías padre disponibles (nivel 1)
    categorias_padre = Categoria.objects.filter(nivel=1, activa=True)

    context = {"categorias_padre": categorias_padre, "titulo": "Crear Categoría"}
    return render(request, "dashboard/categoria/form.html", context)


def categoria_edit(request, categoria_id):
    """Editar categoría existente"""
    categoria = get_object_or_404(Categoria, categoria_id=categoria_id)

    if request.method == "POST":
        try:
            nombre = request.POST.get("nombre")

            categoria.nombre = nombre
            categoria.descripcion = request.POST.get("descripcion", "")
            categoria.slug = slugify(nombre)
            categoria.activa = request.POST.get("activa") == "on"

            # Si cambia la categoría padre, actualizar nivel
            categoria_padre_id = request.POST.get("categoria_padre")
            if categoria_padre_id:
                categoria_padre = Categoria.objects.get(categoria_id=categoria_padre_id)
                categoria.categoria_padre = categoria_padre
                categoria.nivel = categoria_padre.nivel + 1
            else:
                categoria.categoria_padre = None
                categoria.nivel = 1

            categoria.save()

            messages.success(
                request, f'Categoría "{categoria.nombre}" actualizada exitosamente.'
            )
            return redirect("dashboard:categoria_list")

        except Exception as e:
            messages.error(request, f"Error al actualizar categoría: {str(e)}")

    # Obtener categorías padre disponibles (excluyendo la actual y sus hijas)
    categorias_padre = Categoria.objects.filter(nivel=1, activa=True).exclude(
        categoria_id=categoria_id
    )

    context = {
        "categoria": categoria,
        "categorias_padre": categorias_padre,
        "titulo": f"Editar: {categoria.nombre}",
    }
    return render(request, "dashboard/categoria/form.html", context)


def categoria_delete(request, categoria_id):
    """Eliminar categoría"""
    categoria = get_object_or_404(Categoria, categoria_id=categoria_id)

    if request.method == "POST":
        try:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada exitosamente.')
        except Exception as e:
            messages.error(request, f"Error al eliminar categoría: {str(e)}")

        return redirect("dashboard:categoria_list")

    # Verificar si tiene productos asociados
    productos_count = Producto.objects.filter(categoria=categoria).count()
    subcategorias_count = Categoria.objects.filter(categoria_padre=categoria).count()

    context = {
        "categoria": categoria,
        "productos_count": productos_count,
        "subcategorias_count": subcategorias_count,
        "titulo": f"Eliminar: {categoria.nombre}",
    }
    return render(request, "dashboard/categoria/delete.html", context)


# CRUD PRODUCTOS


def producto_list(request):
    """Lista todos los productos"""
    productos = (
        Producto.objects.all()
        .select_related("categoria", "marca")
        .order_by("-fecha_creation")
    )

    # Filtros
    categoria_id = request.GET.get("categoria")
    marca_id = request.GET.get("marca")
    estado = request.GET.get("estado")
    busqueda = request.GET.get("busqueda")

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if marca_id:
        productos = productos.filter(marca_id=marca_id)
    if estado:
        productos = productos.filter(estado_producto=estado)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    # Paginación
    paginator = Paginator(productos, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Datos para filtros
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)

    context = {
        "productos": page_obj,
        "categorias": categorias,
        "marcas": marcas,
        "filtros": {
            "categoria": categoria_id,
            "marca": marca_id,
            "estado": estado,
            "busqueda": busqueda,
        },
        "titulo": "Gestión de Productos",
    }
    return render(request, "dashboard/producto/list.html", context)


def producto_create(request):
    """Crear nuevo producto"""
    if request.method == "POST":
        try:
            logger.info("Iniciando creación de producto")

            categoria_id = request.POST.get("categoria")
            marca_id = request.POST.get("marca")

            categoria = Categoria.objects.get(categoria_id=categoria_id)
            marca = Marca.objects.get(marca_id=marca_id) if marca_id else None

            # Manejar imagen subida
            imagen_url = ""

            if "imagen_file" in request.FILES:
                imagen_file = request.FILES["imagen_file"]
                logger.info(
                    f"Archivo de imagen recibido: {imagen_file.name}, tamaño: {imagen_file.size} bytes"
                )

                # Subir a DigitalOcean Spaces (siempre sin timestamp, solo slug)
                result = upload_product_image(imagen_file, use_unique_name=False)

                if result["success"]:
                    # Guardar solo la ruta relativa (productos/nombre.jpg)
                    imagen_url = result["path"]
                    logger.info(f"Imagen subida exitosamente: {result['path']}")
                    messages.success(
                        request, f"Imagen subida exitosamente: {result['path']}"
                    )
                else:
                    logger.error(f"Error al subir imagen: {result['message']}")
                    messages.warning(
                        request, f"No se pudo subir la imagen: {result['message']}"
                    )
            else:
                logger.info("No se recibió archivo de imagen")

            nombre = request.POST.get("nombre")

            producto = Producto.objects.create(
                categoria=categoria,
                marca=marca,
                sku=request.POST.get("sku"),
                nombre=nombre,
                descripcion=request.POST.get("descripcion", ""),
                precio=int(request.POST.get("precio")),
                stock=int(request.POST.get("stock", 0)),
                imagen_url=imagen_url,
                estado_producto="activo",
                slug=slugify(nombre),
            )

            logger.info(
                f"Producto creado exitosamente: {producto.nombre} (ID: {producto.producto_id})"
            )
            messages.success(
                request, f'Producto "{producto.nombre}" creado exitosamente.'
            )
            return redirect("dashboard:producto_list")

        except Exception as e:
            logger.error(f"Error al crear producto: {str(e)}", exc_info=True)
            messages.error(request, f"Error al crear producto: {str(e)}")

    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)

    context = {"categorias": categorias, "marcas": marcas, "titulo": "Crear Producto"}
    return render(request, "dashboard/producto/form.html", context)


def producto_edit(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, producto_id=producto_id)

    if request.method == "POST":
        try:
            logger.info(
                f"Iniciando edición de producto: {producto.nombre} (ID: {producto_id})"
            )

            categoria_id = request.POST.get("categoria")
            marca_id = request.POST.get("marca")

            nombre = request.POST.get("nombre")

            producto.categoria = Categoria.objects.get(categoria_id=categoria_id)
            producto.marca = Marca.objects.get(marca_id=marca_id) if marca_id else None
            producto.sku = request.POST.get("sku")
            producto.nombre = nombre
            producto.descripcion = request.POST.get("descripcion", "")
            producto.precio = int(request.POST.get("precio"))
            producto.stock = int(request.POST.get("stock", 0))
            producto.estado_producto = request.POST.get("estado_producto")
            producto.slug = slugify(nombre)

            # Verificar si se solicita eliminar la imagen actual
            eliminar_imagen = request.POST.get("eliminar_imagen") == "true"

            if eliminar_imagen and producto.imagen_url:
                logger.info(
                    f"Solicitud de eliminar imagen actual: {producto.imagen_url}"
                )
                imagen_a_eliminar = producto.imagen_url

                # Eliminar imagen del storage
                delete_result = delete_product_image(imagen_a_eliminar)
                if delete_result["success"]:
                    logger.info(f"Imagen eliminada exitosamente: {imagen_a_eliminar}")
                    messages.info(request, f"Imagen eliminada: {imagen_a_eliminar}")
                    producto.imagen_url = ""
                else:
                    logger.warning(
                        f"No se pudo eliminar imagen: {delete_result['message']}"
                    )
                    messages.warning(
                        request,
                        f"No se pudo eliminar la imagen: {delete_result['message']}",
                    )

            # Manejar imagen subida (solo si no se eliminó o si se sube una nueva)
            elif "imagen_file" in request.FILES:
                imagen_file = request.FILES["imagen_file"]
                logger.info(
                    f"Nueva imagen recibida: {imagen_file.name}, tamaño: {imagen_file.size} bytes"
                )

                # Guardar la imagen anterior para eliminarla después
                imagen_anterior = producto.imagen_url
                logger.info(f"Imagen anterior a eliminar: {imagen_anterior}")

                # Subir a DigitalOcean Spaces (siempre sin timestamp, solo slug)
                result = upload_product_image(imagen_file, use_unique_name=False)

                if result["success"]:
                    # Actualizar con la nueva ruta
                    producto.imagen_url = result["path"]
                    logger.info(f"Nueva imagen subida: {result['path']}")
                    messages.success(request, f"Nueva imagen subida: {result['path']}")

                    # Eliminar la imagen anterior si existe y es diferente
                    if imagen_anterior and imagen_anterior != result["path"]:
                        logger.info(
                            f"Intentando eliminar imagen anterior: {imagen_anterior}"
                        )
                        delete_result = delete_product_image(imagen_anterior)
                        if delete_result["success"]:
                            logger.info(f"Imagen anterior eliminada: {imagen_anterior}")
                            messages.info(
                                request, f"Imagen anterior eliminada: {imagen_anterior}"
                            )
                        else:
                            logger.warning(
                                f"No se pudo eliminar imagen anterior: {delete_result['message']}"
                            )
                else:
                    logger.error(f"Error al subir nueva imagen: {result['message']}")
                    messages.warning(
                        request,
                        f"No se pudo subir la nueva imagen: {result['message']}",
                    )

            producto.save()

            logger.info(f"Producto actualizado exitosamente: {producto.nombre}")
            messages.success(
                request, f'Producto "{producto.nombre}" actualizado exitosamente.'
            )
            return redirect("dashboard:producto_list")

        except Exception as e:
            logger.error(f"Error al actualizar producto: {str(e)}", exc_info=True)
            messages.error(request, f"Error al actualizar producto: {str(e)}")

    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)

    context = {
        "producto": producto,
        "categorias": categorias,
        "marcas": marcas,
        "titulo": f"Editar: {producto.nombre}",
    }
    return render(request, "dashboard/producto/form.html", context)


def producto_delete(request, producto_id):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, producto_id=producto_id)

    if request.method == "POST":
        try:
            nombre = producto.nombre
            imagen_url = producto.imagen_url

            logger.info(f"Eliminando producto: {nombre} (ID: {producto_id})")

            # Eliminar producto de la base de datos
            producto.delete()
            logger.info(f"Producto eliminado de la base de datos: {nombre}")

            # Eliminar imagen de Spaces si existe
            if imagen_url:
                logger.info(f"Intentando eliminar imagen del storage: {imagen_url}")
                delete_result = delete_product_image(imagen_url)
                if delete_result["success"]:
                    logger.info(f"Imagen eliminada del storage: {imagen_url}")
                    messages.info(request, f"Imagen eliminada: {imagen_url}")
                else:
                    logger.warning(
                        f"No se pudo eliminar imagen: {delete_result['message']}"
                    )
                    # No mostramos error al usuario porque el producto ya fue eliminado

            messages.success(request, f'Producto "{nombre}" eliminado exitosamente.')
        except Exception as e:
            logger.error(f"Error al eliminar producto: {str(e)}", exc_info=True)
            messages.error(request, f"Error al eliminar producto: {str(e)}")

        return redirect("dashboard:producto_list")

    context = {"producto": producto, "titulo": f"Eliminar: {producto.nombre}"}
    return render(request, "dashboard/producto/delete.html", context)


# CRUD COSTOS DE ENVÍO


def costo_envio_list(request):
    """Listado de costos de envío por comuna"""
    costos = CostoEnvioComuna.objects.all().order_by("comuna")

    # Búsqueda
    search = request.GET.get("search", "")
    if search:
        costos = costos.filter(comuna__icontains=search)

    # Filtro por estado
    estado = request.GET.get("estado", "")
    if estado == "activo":
        costos = costos.filter(activo=True)
    elif estado == "inactivo":
        costos = costos.filter(activo=False)

    # Paginación
    paginator = Paginator(costos, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "estado": estado,
        "total_costos": costos.count(),
    }
    return render(request, "dashboard/costo_envio/list.html", context)


def costo_envio_create(request):
    """Crear nuevo costo de envío"""
    if request.method == "POST":
        try:
            comuna = request.POST.get("comuna", "").strip()
            costo = request.POST.get("costo", "").strip()
            activo = request.POST.get("activo") == "on"

            # Validaciones
            if not comuna:
                messages.error(request, "El nombre de la comuna es obligatorio.")
                return render(
                    request,
                    "dashboard/costo_envio/create.html",
                    {"comuna": comuna, "costo": costo},
                )

            if not costo or not costo.isdigit():
                messages.error(request, "El costo debe ser un número válido.")
                return render(
                    request,
                    "dashboard/costo_envio/create.html",
                    {"comuna": comuna, "costo": costo},
                )

            # Verificar si ya existe
            if CostoEnvioComuna.objects.filter(comuna__iexact=comuna).exists():
                messages.error(
                    request, f'Ya existe un costo de envío para la comuna "{comuna}".'
                )
                return render(
                    request,
                    "dashboard/costo_envio/create.html",
                    {"comuna": comuna, "costo": costo},
                )

            # Crear costo de envío
            CostoEnvioComuna.objects.create(
                comuna=comuna.title(), costo=int(costo), activo=activo
            )

            messages.success(
                request, f'Costo de envío para "{comuna}" creado exitosamente.'
            )
            return redirect("dashboard:costo_envio_list")

        except Exception as e:
            logger.error(f"Error al crear costo de envío: {str(e)}", exc_info=True)
            messages.error(request, f"Error al crear costo de envío: {str(e)}")

    return render(request, "dashboard/costo_envio/create.html")


def costo_envio_edit(request, costo_id):
    """Editar costo de envío"""
    costo_envio = get_object_or_404(CostoEnvioComuna, id=costo_id)

    if request.method == "POST":
        try:
            comuna = request.POST.get("comuna", "").strip()
            costo = request.POST.get("costo", "").strip()
            activo = request.POST.get("activo") == "on"

            # Validaciones
            if not comuna:
                messages.error(request, "El nombre de la comuna es obligatorio.")
                return render(
                    request,
                    "dashboard/costo_envio/edit.html",
                    {"costo_envio": costo_envio},
                )

            if not costo or not costo.isdigit():
                messages.error(request, "El costo debe ser un número válido.")
                return render(
                    request,
                    "dashboard/costo_envio/edit.html",
                    {"costo_envio": costo_envio},
                )

            # Verificar si ya existe otra comuna con el mismo nombre
            existe = (
                CostoEnvioComuna.objects.filter(comuna__iexact=comuna)
                .exclude(id=costo_id)
                .exists()
            )
            if existe:
                messages.error(
                    request, f'Ya existe un costo de envío para la comuna "{comuna}".'
                )
                return render(
                    request,
                    "dashboard/costo_envio/edit.html",
                    {"costo_envio": costo_envio},
                )

            # Actualizar
            costo_envio.comuna = comuna.title()
            costo_envio.costo = int(costo)
            costo_envio.activo = activo
            costo_envio.save()

            messages.success(
                request, f'Costo de envío para "{comuna}" actualizado exitosamente.'
            )
            return redirect("dashboard:costo_envio_list")

        except Exception as e:
            logger.error(f"Error al actualizar costo de envío: {str(e)}", exc_info=True)
            messages.error(request, f"Error al actualizar costo de envío: {str(e)}")

    context = {
        "costo_envio": costo_envio,
    }
    return render(request, "dashboard/costo_envio/edit.html", context)


def costo_envio_delete(request, costo_id):
    """Eliminar costo de envío"""
    costo_envio = get_object_or_404(CostoEnvioComuna, id=costo_id)

    if request.method == "POST":
        try:
            comuna = costo_envio.comuna
            costo_envio.delete()
            messages.success(
                request, f'Costo de envío para "{comuna}" eliminado exitosamente.'
            )
        except Exception as e:
            logger.error(f"Error al eliminar costo de envío: {str(e)}", exc_info=True)
            messages.error(request, f"Error al eliminar costo de envío: {str(e)}")

        return redirect("dashboard:costo_envio_list")

    context = {
        "costo_envio": costo_envio,
    }
    return render(request, "dashboard/costo_envio/delete.html", context)


def costo_envio_cargar_predeterminados(request):
    """Cargar costos predeterminados para las comunas de Santiago"""
    if request.method == "POST":
        try:
            costos_predeterminados = {
                "Quilicura": 4000,
                "Huechuraba": 4500,
                "Vitacura": 4500,
                "Providencia": 4000,
                "La Reina": 4000,
                "Ñuñoa": 4000,
                "Macul": 3500,
                "San Joaquín": 2000,
                "La Florida": 3500,
                "San Miguel": 0,
                "Pedro Aguirre Cerda": 2000,
                "Cerro Navia": 4000,
                "Estación Central": 3500,
                "Quinta Normal": 4000,
                "Maipú": 4000,
                "Pudahuel": 4000,
                "Lo Prado": 4000,
                "Cerrillos": 3500,
                "La Pintana": 3500,
                "El Bosque": 3500,
                "San Bernardo": 4000,
                "La Cisterna": 1500,
                "San José de Maipo": 3500,
                "Peñalolén": 4000,
                "Lo Espejo": 3500,
                "Puente Alto": 3500,
                "San Ramón": 2000,
                "Conchalí": 4000,
                "Recoleta": 4000,
                "Renca": 4000,
                "Independencia": 4000,
                "La Granja": 3000,
                "Pirque": 3500,
                "Lo Barnechea": 4500,
                "Las Condes": 4500,
                "Padre Hurtado": 4000,
            }

            creados = 0
            actualizados = 0

            for comuna, costo in costos_predeterminados.items():
                costo_obj, created = CostoEnvioComuna.objects.update_or_create(
                    comuna=comuna, defaults={"costo": costo, "activo": True}
                )
                if created:
                    creados += 1
                else:
                    actualizados += 1

            messages.success(
                request,
                f"Costos predeterminados cargados: {creados} creados, {actualizados} actualizados.",
            )
        except Exception as e:
            logger.error(
                f"Error al cargar costos predeterminados: {str(e)}", exc_info=True
            )
            messages.error(request, f"Error al cargar costos predeterminados: {str(e)}")

        return redirect("dashboard:costo_envio_list")

    return render(request, "dashboard/costo_envio/cargar_predeterminados.html")


# REPORTES DE VENTAS Y PRODUCTOS


def reportes_ventas(request):
    """Vista principal de reportes de ventas"""
    # Obtener parámetros de filtrado
    periodo = request.GET.get("periodo", "mes")  # dia, semana, mes, trimestre, año
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    print("perdiodo: " + periodo)
    # Calcular fechas según período
    today = timezone.now().date()

    if periodo == "dia":
        start_date = today
        end_date = today
    elif periodo == "semana":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif periodo == "mes":
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(
                days=1
            )
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif periodo == "trimestre":
        quarter = (today.month - 1) // 3 + 1
        start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
        end_date = (start_date + timedelta(days=93)).replace(day=1) - timedelta(days=1)
    elif periodo == "año":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        # Período personalizado
        if fecha_inicio and fecha_fin:
            start_date = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            end_date = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        else:
            start_date = today.replace(day=1)
            end_date = today

    # Métricas generales de ventas
    ventas_stats = Pedido.objects.filter(
        fecha__date__gte=start_date, fecha__date__lte=end_date, estado__in=["Entregado"]
    ).aggregate(
        total_ventas=Coalesce(Sum("total"), Value(0)),
        num_pedidos=Count("pedido_id"),
        ticket_promedio=Coalesce(Avg("total"), Value(0.0)),
    )

    # Ventas por día (para gráfico)
    ventas_diarias = (
        Pedido.objects.filter(
            fecha__date__gte=start_date,
            fecha__date__lte=end_date,
            estado__in=["Entregado"],
        )
        .values("fecha__date")
        .annotate(total=Coalesce(Sum("total"), Value(0)), pedidos=Count("pedido_id"))
        .order_by("fecha__date")
    )

    # Top productos vendidos
    productos_vendidos = (
        PedidoItem.objects.filter(
            pedido__fecha__date__gte=start_date, pedido__fecha__date__lte=end_date
        )
        .filter(pedido__estado__in=["Entregado"])
        .values(
            "producto__nombre",
            "producto__sku",
            "producto__precio",
            "producto__categoria__nombre",
        )
        .annotate(
            cantidad_vendida=Sum("cantidad"),
            ingresos_totales=Sum(
                F("cantidad") * F("precio_unitario"), output_field=IntegerField()
            ),
            num_pedidos=Count("pedido", distinct=True),
        )
        .order_by("-cantidad_vendida")[:10]
    )

    # Ventas por categoría
    ventas_por_categoria = (
        PedidoItem.objects.filter(
            pedido__fecha__date__gte=start_date, pedido__fecha__date__lte=end_date
        )
        .filter(pedido__estado__in=["Entregado"])
        .values("producto__categoria__nombre")
        .annotate(
            total_ventas=Sum(
                F("cantidad") * F("precio_unitario"), output_field=IntegerField()
            ),
            cantidad_vendida=Sum("cantidad"),
        )
        .order_by("-total_ventas")
    )

    # Estados de pedidos
    estados_pedidos = (
        Pedido.objects.filter(fecha__date__gte=start_date, fecha__date__lte=end_date)
        .values("estado")
        .annotate(count=Count("pedido_id"))
        .order_by("-count")
    )

    # Clientes top
    clientes_top = (
        Pedido.objects.filter(
            fecha__date__gte=start_date,
            fecha__date__lte=end_date,
            estado__in=["Entregado"],
        )
        .values(
            "cliente_persona__nombres",
            "cliente_persona__apellido_paterno",
            "cliente_persona__email",
            "cliente_empresa__razon_social",
            "cliente_empresa__email_contacto",
        )
        .annotate(total_compras=Sum("total"), num_pedidos=Count("pedido_id"))
        .order_by("-total_compras")[:10]
    )

    # Serializar ventas_diarias a tipos JSON-serializables para evitar que
    # objetos de Python (e.g., datetime.date o Decimal) se inyecten en JS
    ventas_diarias_list = list(ventas_diarias)
    ventas_diarias_serialized = []
    for v in ventas_diarias_list:
        fecha = v.get("fecha__date")
        # convertir fecha a ISO string si es un objeto date/datetime
        if hasattr(fecha, "isoformat"):
            fecha_str = fecha.isoformat()
        else:
            fecha_str = str(fecha) if fecha is not None else ""

        total = v.get("total", 0)
        try:
            total_val = float(total)
        except Exception:
            # fallback a 0.0 si no es convertible
            try:
                total_val = float(str(total))
            except Exception:
                total_val = 0.0

        pedidos = v.get("pedidos", 0)
        try:
            pedidos_val = int(pedidos)
        except Exception:
            try:
                pedidos_val = int(str(pedidos))
            except Exception:
                pedidos_val = 0

        ventas_diarias_serialized.append(
            {
                "fecha__date": fecha_str,
                "total": total_val,
                "pedidos": pedidos_val,
            }
        )

    context = {
        "periodo": periodo,
        "start_date": start_date,
        "end_date": end_date,
        "ventas_stats": ventas_stats,
        "ventas_diarias": ventas_diarias_serialized,
        "productos_vendidos": productos_vendidos,
        "ventas_por_categoria": ventas_por_categoria,
        "estados_pedidos": estados_pedidos,
        "clientes_top": clientes_top,
    }

    return render(request, "dashboard/reportes/ventas.html", context)


def reportes_productos(request):
    """Vista principal de reportes de productos"""
    # Obtener parámetros de filtrado
    categoria_id = request.GET.get("categoria")
    marca_id = request.GET.get("marca")
    orden = request.GET.get("orden", "ventas")  # ventas, stock, precio, nombre

    # Base query
    productos_query = Producto.objects.select_related("categoria", "marca")

    # Filtros
    if categoria_id:
        productos_query = productos_query.filter(categoria_id=categoria_id)
    if marca_id:
        productos_query = productos_query.filter(marca_id=marca_id)

    # Agregar métricas de ventas (últimos 30 días)
    fecha_limite = timezone.now().date() - timedelta(days=30)

    productos_con_ventas = productos_query.annotate(
        total_vendido=Coalesce(
            Sum(
                "pedidoitem__cantidad",
                filter=Q(
                    pedidoitem__pedido__fecha__date__gte=fecha_limite,
                    pedidoitem__pedido__estado__in=["Entregado"],
                ),
            ),
            0,
        ),
        ingresos_generados=Coalesce(
            Sum(
                F("pedidoitem__cantidad") * F("pedidoitem__precio_unitario"),
                filter=Q(
                    pedidoitem__pedido__fecha__date__gte=fecha_limite,
                    pedidoitem__pedido__estado__in=["Entregado"],
                ),
            ),
            0,
        ),
        num_pedidos=Count(
            "pedidoitem__pedido",
            filter=Q(
                pedidoitem__pedido__fecha__date__gte=fecha_limite,
                pedidoitem__pedido__estado__in=["Entregado"],
            ),
            distinct=True,
        ),
    )

    # Ordenamiento
    if orden == "ventas":
        productos_con_ventas = productos_con_ventas.order_by("-total_vendido")
    elif orden == "ingresos":
        productos_con_ventas = productos_con_ventas.order_by("-ingresos_generados")
    elif orden == "stock":
        productos_con_ventas = productos_con_ventas.order_by("stock")
    elif orden == "precio":
        productos_con_ventas = productos_con_ventas.order_by("-precio")
    else:
        productos_con_ventas = productos_con_ventas.order_by("nombre")

    # Paginación
    paginator = Paginator(productos_con_ventas, 20)
    page_number = request.GET.get("page")
    productos_paginados = paginator.get_page(page_number)

    # Estadísticas generales
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(estado_producto="activo").count()
    productos_stock_bajo = Producto.objects.filter(
        stock__lt=10, estado_producto="activo"
    ).count()
    productos_sin_stock = Producto.objects.filter(
        stock=0, estado_producto="activo"
    ).count()

    # Valor total del inventario
    valor_inventario = Producto.objects.filter(estado_producto="activo").aggregate(
        valor_total=Coalesce(Sum(F("stock") * F("precio")), 0)
    )["valor_total"]

    # Productos más vendidos (todos los tiempos)
    productos_mas_vendidos = (
        PedidoItem.objects.filter(pedido__estado__in=["Entregado"])
        .values("producto__nombre", "producto__sku", "producto__precio")
        .annotate(
            total_vendido=Sum("cantidad"),
            ingresos=Sum(F("cantidad") * F("precio_unitario")),
        )
        .order_by("-total_vendido")[:10]
    )

    # Categorías con más productos
    categorias_stats = Categoria.objects.annotate(
        num_productos=Count("producto", filter=Q(producto__estado_producto="activo")),
        productos_stock_bajo=Count(
            "producto",
            filter=Q(producto__stock__lt=10, producto__estado_producto="activo"),
        ),
    ).order_by("-num_productos")

    # Para los filtros
    categorias = Categoria.objects.filter(activa=True).order_by("nombre")
    marcas = Marca.objects.filter(activa=True).order_by("nombre")

    context = {
        "productos": productos_paginados,
        "total_productos": total_productos,
        "productos_activos": productos_activos,
        "productos_stock_bajo": productos_stock_bajo,
        "productos_sin_stock": productos_sin_stock,
        "valor_inventario": valor_inventario,
        "productos_mas_vendidos": productos_mas_vendidos,
        "categorias_stats": categorias_stats,
        "categorias": categorias,
        "marcas": marcas,
        "categoria_seleccionada": categoria_id,
        "marca_seleccionada": marca_id,
        "orden_seleccionado": orden,
    }

    return render(request, "dashboard/reportes/productos.html", context)


def api_ventas_chart(request):
    """API para datos de gráfico de ventas"""
    periodo = request.GET.get("periodo", "mes")

    today = timezone.now().date()

    if periodo == "dia":
        # Últimas 24 horas por hora
        start_datetime = timezone.now() - timedelta(hours=24)
        ventas = (
            Pedido.objects.filter(fecha__gte=start_datetime, estado__in=["Entregado"])
            .extra(select={"hour": "EXTRACT(hour FROM fecha)"})
            .values("hour")
            .annotate(total=Coalesce(Sum("total"), 0))
            .order_by("hour")
        )

        data = {
            "labels": [f"{int(v['hour'])}:00" for v in ventas],
            "data": [float(v["total"]) for v in ventas],
        }

    elif periodo == "semana":
        # Últimos 7 días
        start_date = today - timedelta(days=6)
        ventas = (
            Pedido.objects.filter(
                fecha__date__gte=start_date,
                fecha__date__lte=today,
                estado__in=["Entregado"],
            )
            .values("fecha__date")
            .annotate(total=Coalesce(Sum("total"), 0))
            .order_by("fecha__date")
        )

        data = {
            "labels": [v["fecha__date"].strftime("%d/%m") for v in ventas],
            "data": [float(v["total"]) for v in ventas],
        }

    elif periodo == "mes":
        # Últimos 30 días
        start_date = today - timedelta(days=29)
        ventas = (
            Pedido.objects.filter(
                fecha__date__gte=start_date,
                fecha__date__lte=today,
                estado__in=["Entregado"],
            )
            .values("fecha__date")
            .annotate(total=Coalesce(Sum("total"), 0))
            .order_by("fecha__date")
        )

        data = {
            "labels": [v["fecha__date"].strftime("%d/%m") for v in ventas],
            "data": [float(v["total"]) for v in ventas],
        }

    else:  # año
        # Últimos 12 meses
        ventas = (
            Pedido.objects.filter(
                fecha__gte=today.replace(day=1) - timedelta(days=365),
                estado__in=["Entregado"],
            )
            .annotate(mes=TruncMonth("fecha"))
            .values("mes")
            .annotate(total=Coalesce(Sum("total"), 0))
            .order_by("mes")
        )

        data = {
            "labels": [v["mes"].strftime("%m/%Y") for v in ventas],
            "data": [float(v["total"]) for v in ventas],
        }

    return JsonResponse(data)


def api_categorias_chart(request):
    """API para datos de gráfico de ventas por categoría"""
    # Últimos 30 días
    fecha_limite = timezone.now().date() - timedelta(days=30)

    ventas_categoria = (
        PedidoItem.objects.filter(
            pedido__fecha__date__gte=fecha_limite, pedido__estado__in=["Entregado"]
        )
        .values("producto__categoria__nombre")
        .annotate(total=Sum(F("cantidad") * F("precio_unitario")))
        .order_by("-total")[:10]
    )

    data = {
        "labels": [
            v["producto__categoria__nombre"] or "Sin categoría"
            for v in ventas_categoria
        ],
        "data": [float(v["total"]) for v in ventas_categoria],
    }

    return JsonResponse(data)
