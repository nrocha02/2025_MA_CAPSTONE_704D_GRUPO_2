from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from apps.ventas.models import Producto, Categoria, Marca
from .storage import upload_product_image, delete_product_image, is_spaces_configured
import logging

# Configurar logger
logger = logging.getLogger(__name__)


def admin_dashboard(request):
    """Dashboard principal de administración"""
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(estado_producto='activo').count()
    total_categorias = Categoria.objects.count()
    categorias_activas = Categoria.objects.filter(activa=True).count()
    total_marcas = Marca.objects.count()
    marcas_activas = Marca.objects.filter(activa=True).count()
    
    # Productos con stock bajo (menos de 10)
    productos_stock_bajo = Producto.objects.filter(stock__lt=10, estado_producto='activo').count()
    
    context = {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'total_categorias': total_categorias,
        'categorias_activas': categorias_activas,
        'total_marcas': total_marcas,
        'marcas_activas': marcas_activas,
        'productos_stock_bajo': productos_stock_bajo,
    }
    return render(request, 'dashboard/admin/dashboard.html', context)



# CRUD CATEGORÍAS


def categoria_list(request):
    """Lista todas las categorías"""
    from django.db.models import Count
    
    categorias = Categoria.objects.annotate(
        productos_count=Count('producto')
    ).order_by('nivel', 'nombre')
    
    # Paginación
    paginator = Paginator(categorias, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categorias': page_obj,
        'titulo': 'Gestión de Categorías'
    }
    return render(request, 'dashboard/categoria/list.html', context)


def categoria_create(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            categoria_padre_id = request.POST.get('categoria_padre')
            slug = request.POST.get('slug', '')
            
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
                slug=slug,
                activa=True
            )
            
            messages.success(request, f'Categoría "{nombre}" creada exitosamente.')
            return redirect('dashboard:categoria_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear categoría: {str(e)}')
    
    # Obtener categorías padre disponibles (nivel 1)
    categorias_padre = Categoria.objects.filter(nivel=1, activa=True)
    
    context = {
        'categorias_padre': categorias_padre,
        'titulo': 'Crear Categoría'
    }
    return render(request, 'dashboard/categoria/form.html', context)


def categoria_edit(request, categoria_id):
    """Editar categoría existente"""
    categoria = get_object_or_404(Categoria, categoria_id=categoria_id)
    
    if request.method == 'POST':
        try:
            categoria.nombre = request.POST.get('nombre')
            categoria.descripcion = request.POST.get('descripcion', '')
            categoria.slug = request.POST.get('slug', '')
            categoria.activa = request.POST.get('activa') == 'on'
            
            # Si cambia la categoría padre, actualizar nivel
            categoria_padre_id = request.POST.get('categoria_padre')
            if categoria_padre_id:
                categoria_padre = Categoria.objects.get(categoria_id=categoria_padre_id)
                categoria.categoria_padre = categoria_padre
                categoria.nivel = categoria_padre.nivel + 1
            else:
                categoria.categoria_padre = None
                categoria.nivel = 1
            
            categoria.save()
            
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente.')
            return redirect('dashboard:categoria_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar categoría: {str(e)}')
    
    # Obtener categorías padre disponibles (excluyendo la actual y sus hijas)
    categorias_padre = Categoria.objects.filter(nivel=1, activa=True).exclude(categoria_id=categoria_id)
    
    context = {
        'categoria': categoria,
        'categorias_padre': categorias_padre,
        'titulo': f'Editar: {categoria.nombre}'
    }
    return render(request, 'dashboard/categoria/form.html', context)


def categoria_delete(request, categoria_id):
    """Eliminar categoría"""
    categoria = get_object_or_404(Categoria, categoria_id=categoria_id)
    
    if request.method == 'POST':
        try:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar categoría: {str(e)}')
        
        return redirect('dashboard:categoria_list')
    
    # Verificar si tiene productos asociados
    productos_count = Producto.objects.filter(categoria=categoria).count()
    subcategorias_count = Categoria.objects.filter(categoria_padre=categoria).count()
    
    context = {
        'categoria': categoria,
        'productos_count': productos_count,
        'subcategorias_count': subcategorias_count,
        'titulo': f'Eliminar: {categoria.nombre}'
    }
    return render(request, 'dashboard/categoria/delete.html', context)



# CRUD PRODUCTOS


def producto_list(request):
    """Lista todos los productos"""
    productos = Producto.objects.all().select_related('categoria', 'marca').order_by('-fecha_creation')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    estado = request.GET.get('estado')
    busqueda = request.GET.get('busqueda')
    
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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'productos': page_obj,
        'categorias': categorias,
        'marcas': marcas,
        'filtros': {
            'categoria': categoria_id,
            'marca': marca_id,
            'estado': estado,
            'busqueda': busqueda,
        },
        'titulo': 'Gestión de Productos'
    }
    return render(request, 'dashboard/producto/list.html', context)


def producto_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            logger.info("Iniciando creación de producto")
            
            categoria_id = request.POST.get('categoria')
            marca_id = request.POST.get('marca')
            
            categoria = Categoria.objects.get(categoria_id=categoria_id)
            marca = Marca.objects.get(marca_id=marca_id) if marca_id else None
            
            # Manejar imagen subida
            imagen_url = ''
            
            if 'imagen_file' in request.FILES:
                imagen_file = request.FILES['imagen_file']
                logger.info(f"Archivo de imagen recibido: {imagen_file.name}, tamaño: {imagen_file.size} bytes")
                
                # Subir a DigitalOcean Spaces (siempre sin timestamp, solo slug)
                result = upload_product_image(imagen_file, use_unique_name=False)
                
                if result['success']:
                    # Guardar solo la ruta relativa (productos/nombre.jpg)
                    imagen_url = result['path']
                    logger.info(f"Imagen subida exitosamente: {result['path']}")
                    messages.success(request, f'Imagen subida exitosamente: {result["path"]}')
                else:
                    logger.error(f"Error al subir imagen: {result['message']}")
                    messages.warning(request, f'No se pudo subir la imagen: {result["message"]}')
            else:
                logger.info("No se recibió archivo de imagen")
            
            producto = Producto.objects.create(
                categoria=categoria,
                marca=marca,
                sku=request.POST.get('sku'),
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion', ''),
                precio=int(request.POST.get('precio')),
                stock=int(request.POST.get('stock', 0)),
                imagen_url=imagen_url,
                estado_producto='activo'
            )
            
            logger.info(f"Producto creado exitosamente: {producto.nombre} (ID: {producto.producto_id})")
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('dashboard:producto_list')
            
        except Exception as e:
            logger.error(f"Error al crear producto: {str(e)}", exc_info=True)
            messages.error(request, f'Error al crear producto: {str(e)}')
    
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'categorias': categorias,
        'marcas': marcas,
        'titulo': 'Crear Producto'
    }
    return render(request, 'dashboard/producto/form.html', context)


def producto_edit(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, producto_id=producto_id)
    
    if request.method == 'POST':
        try:
            logger.info(f"Iniciando edición de producto: {producto.nombre} (ID: {producto_id})")
            
            categoria_id = request.POST.get('categoria')
            marca_id = request.POST.get('marca')
            
            producto.categoria = Categoria.objects.get(categoria_id=categoria_id)
            producto.marca = Marca.objects.get(marca_id=marca_id) if marca_id else None
            producto.sku = request.POST.get('sku')
            producto.nombre = request.POST.get('nombre')
            producto.descripcion = request.POST.get('descripcion', '')
            producto.precio = int(request.POST.get('precio'))
            producto.stock = int(request.POST.get('stock', 0))
            producto.estado_producto = request.POST.get('estado_producto')
            
            # Verificar si se solicita eliminar la imagen actual
            eliminar_imagen = request.POST.get('eliminar_imagen') == 'true'
            
            if eliminar_imagen and producto.imagen_url:
                logger.info(f"Solicitud de eliminar imagen actual: {producto.imagen_url}")
                imagen_a_eliminar = producto.imagen_url
                
                # Eliminar imagen del storage
                delete_result = delete_product_image(imagen_a_eliminar)
                if delete_result['success']:
                    logger.info(f"Imagen eliminada exitosamente: {imagen_a_eliminar}")
                    messages.info(request, f'Imagen eliminada: {imagen_a_eliminar}')
                    producto.imagen_url = ''
                else:
                    logger.warning(f"No se pudo eliminar imagen: {delete_result['message']}")
                    messages.warning(request, f'No se pudo eliminar la imagen: {delete_result["message"]}')
            
            # Manejar imagen subida (solo si no se eliminó o si se sube una nueva)
            elif 'imagen_file' in request.FILES:
                imagen_file = request.FILES['imagen_file']
                logger.info(f"Nueva imagen recibida: {imagen_file.name}, tamaño: {imagen_file.size} bytes")
                
                # Guardar la imagen anterior para eliminarla después
                imagen_anterior = producto.imagen_url
                logger.info(f"Imagen anterior a eliminar: {imagen_anterior}")
                
                # Subir a DigitalOcean Spaces (siempre sin timestamp, solo slug)
                result = upload_product_image(imagen_file, use_unique_name=False)
                
                if result['success']:
                    # Actualizar con la nueva ruta
                    producto.imagen_url = result['path']
                    logger.info(f"Nueva imagen subida: {result['path']}")
                    messages.success(request, f'Nueva imagen subida: {result["path"]}')
                    
                    # Eliminar la imagen anterior si existe y es diferente
                    if imagen_anterior and imagen_anterior != result['path']:
                        logger.info(f"Intentando eliminar imagen anterior: {imagen_anterior}")
                        delete_result = delete_product_image(imagen_anterior)
                        if delete_result['success']:
                            logger.info(f"Imagen anterior eliminada: {imagen_anterior}")
                            messages.info(request, f'Imagen anterior eliminada: {imagen_anterior}')
                        else:
                            logger.warning(f"No se pudo eliminar imagen anterior: {delete_result['message']}")
                else:
                    logger.error(f"Error al subir nueva imagen: {result['message']}")
                    messages.warning(request, f'No se pudo subir la nueva imagen: {result["message"]}')
            
            producto.save()
            
            logger.info(f"Producto actualizado exitosamente: {producto.nombre}")
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('dashboard:producto_list')
            
        except Exception as e:
            logger.error(f"Error al actualizar producto: {str(e)}", exc_info=True)
            messages.error(request, f'Error al actualizar producto: {str(e)}')
    
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'marcas': marcas,
        'titulo': f'Editar: {producto.nombre}'
    }
    return render(request, 'dashboard/producto/form.html', context)


def producto_delete(request, producto_id):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, producto_id=producto_id)
    
    if request.method == 'POST':
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
                if delete_result['success']:
                    logger.info(f"Imagen eliminada del storage: {imagen_url}")
                    messages.info(request, f'Imagen eliminada: {imagen_url}')
                else:
                    logger.warning(f"No se pudo eliminar imagen: {delete_result['message']}")
                    # No mostramos error al usuario porque el producto ya fue eliminado
            
            messages.success(request, f'Producto "{nombre}" eliminado exitosamente.')
        except Exception as e:
            logger.error(f"Error al eliminar producto: {str(e)}", exc_info=True)
            messages.error(request, f'Error al eliminar producto: {str(e)}')
        
        return redirect('dashboard:producto_list')
    
    context = {
        'producto': producto,
        'titulo': f'Eliminar: {producto.nombre}'
    }
    return render(request, 'dashboard/producto/delete.html', context)
