from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Producto, Categoria, Marca

def index(request):
    # Obtener productos recomendados (los primeros 8 productos activos)
    productos_recomendados = Producto.objects.filter(
        estado_producto='activo'
    ).select_related('categoria', 'marca')[:8]
    
    # Obtener marcas activas para mostrar en la página principal
    marcas = Marca.objects.filter(activa=True)[:5]
    
    context = {
        'productos': productos_recomendados,
        'marcas': marcas,
    }
    return render(request, 'ventas/index.html', context)
    
def producto(request, producto_id):
    # Vista para un producto específico
    producto = get_object_or_404(Producto, producto_id=producto_id, estado_producto='activo')
    
    # Productos relacionados de la misma categoría
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        estado_producto='activo'
    ).exclude(producto_id=producto_id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'ventas/producto.html', context)

def catalogo(request):
    # Obtener todos los productos activos
    productos = Producto.objects.filter(
        estado_producto='activo'
    ).select_related('categoria', 'marca')
    
    # Filtros opcionales
    categoria_id = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if marca_id:
        productos = productos.filter(marca_id=marca_id)
    
    # Obtener todas las categorías y marcas para los filtros
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'categoria_seleccionada': categoria_id,
        'marca_seleccionada': marca_id,
    }
    return render(request, 'ventas/catalogo.html', context)

def carrito(request):
    context = {}
    return render(request, 'ventas/carrito.html', context)

def perro(request):
    # Productos específicos para perros
    categoria_perro = Categoria.objects.filter(nombre__icontains='perro').first()
    productos_perro = Producto.objects.filter(
        categoria=categoria_perro,
        estado_producto='activo'
    ).select_related('marca') if categoria_perro else Producto.objects.none()
    
    context = {
        'productos': productos_perro,
        'categoria': 'Perro',
        'categoria_obj': categoria_perro,
    }
    return render(request, 'ventas/perro.html', context)

def gato(request):
    # Productos específicos para gatos
    categoria_gato = Categoria.objects.filter(nombre__icontains='gato').first()
    productos_gato = Producto.objects.filter(
        categoria=categoria_gato,
        estado_producto='activo'
    ).select_related('marca') if categoria_gato else Producto.objects.none()
    
    context = {
        'productos': productos_gato,
        'categoria': 'Gato',
        'categoria_obj': categoria_gato,
    }
    return render(request, 'ventas/gato.html', context)

def arena(request):
    # Productos específicos para arenas sanitarias
    categoria_arena = Categoria.objects.filter(nombre__icontains='arena').first()
    productos_arena = Producto.objects.filter(
        categoria=categoria_arena,
        estado_producto='activo'
    ).select_related('marca') if categoria_arena else Producto.objects.none()
    
    context = {
        'productos': productos_arena,
        'categoria': 'Arena Sanitaria',
        'categoria_obj': categoria_arena,
    }
    return render(request, 'ventas/arena.html', context)



# VISTAS CRUD PARA ADMINISTRACIÓN/TESTEO


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
    return render(request, 'ventas/admin/dashboard.html', context)



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
    return render(request, 'ventas/admin/categoria_list.html', context)


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
            return redirect('categoria_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear categoría: {str(e)}')
    
    # Obtener categorías padre disponibles (nivel 1)
    categorias_padre = Categoria.objects.filter(nivel=1, activa=True)
    
    context = {
        'categorias_padre': categorias_padre,
        'titulo': 'Crear Categoría'
    }
    return render(request, 'ventas/admin/categoria_form.html', context)


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
            return redirect('categoria_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar categoría: {str(e)}')
    
    # Obtener categorías padre disponibles (excluyendo la actual y sus hijas)
    categorias_padre = Categoria.objects.filter(nivel=1, activa=True).exclude(categoria_id=categoria_id)
    
    context = {
        'categoria': categoria,
        'categorias_padre': categorias_padre,
        'titulo': f'Editar: {categoria.nombre}'
    }
    return render(request, 'ventas/admin/categoria_form.html', context)


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
        
        return redirect('categoria_list')
    
    # Verificar si tiene productos asociados
    productos_count = Producto.objects.filter(categoria=categoria).count()
    subcategorias_count = Categoria.objects.filter(categoria_padre=categoria).count()
    
    context = {
        'categoria': categoria,
        'productos_count': productos_count,
        'subcategorias_count': subcategorias_count,
        'titulo': f'Eliminar: {categoria.nombre}'
    }
    return render(request, 'ventas/admin/categoria_delete.html', context)



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
    return render(request, 'ventas/admin/producto_list.html', context)


def producto_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            categoria_id = request.POST.get('categoria')
            marca_id = request.POST.get('marca')
            
            categoria = Categoria.objects.get(categoria_id=categoria_id)
            marca = Marca.objects.get(marca_id=marca_id) if marca_id else None
            
            producto = Producto.objects.create(
                categoria=categoria,
                marca=marca,
                sku=request.POST.get('sku'),
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion', ''),
                precio=int(request.POST.get('precio')),
                stock=int(request.POST.get('stock', 0)),
                imagen_url=request.POST.get('imagen_url', ''),
                estado_producto='activo'
            )
            
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('producto_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
    
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'categorias': categorias,
        'marcas': marcas,
        'titulo': 'Crear Producto'
    }
    return render(request, 'ventas/admin/producto_form.html', context)


def producto_edit(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, producto_id=producto_id)
    
    if request.method == 'POST':
        try:
            categoria_id = request.POST.get('categoria')
            marca_id = request.POST.get('marca')
            
            producto.categoria = Categoria.objects.get(categoria_id=categoria_id)
            producto.marca = Marca.objects.get(marca_id=marca_id) if marca_id else None
            producto.sku = request.POST.get('sku')
            producto.nombre = request.POST.get('nombre')
            producto.descripcion = request.POST.get('descripcion', '')
            producto.precio = int(request.POST.get('precio'))
            producto.stock = int(request.POST.get('stock', 0))
            producto.imagen_url = request.POST.get('imagen_url', '')
            producto.estado_producto = request.POST.get('estado_producto')
            
            producto.save()
            
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('producto_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar producto: {str(e)}')
    
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'marcas': marcas,
        'titulo': f'Editar: {producto.nombre}'
    }
    return render(request, 'ventas/admin/producto_form.html', context)


def producto_delete(request, producto_id):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, producto_id=producto_id)
    
    if request.method == 'POST':
        try:
            nombre = producto.nombre
            producto.delete()
            messages.success(request, f'Producto "{nombre}" eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar producto: {str(e)}')
        
        return redirect('producto_list')
    
    context = {
        'producto': producto,
        'titulo': f'Eliminar: {producto.nombre}'
    }
    return render(request, 'ventas/admin/producto_delete.html', context)


