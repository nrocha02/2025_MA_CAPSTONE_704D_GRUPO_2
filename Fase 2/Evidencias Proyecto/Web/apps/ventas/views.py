from django.shortcuts import render, get_object_or_404
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
    categoria_nombre = request.GET.get('categoria_nombre')
    marca_id = request.GET.get('marca')
    
    # Filtrar por ID de categoría
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    # Filtrar por nombre de categoría (para los botones de perro/gato)
    elif categoria_nombre:
        categoria_obj = Categoria.objects.filter(nombre__iexact=categoria_nombre, activa=True).first()
        if categoria_obj:
            productos = productos.filter(categoria=categoria_obj)
            categoria_id = str(categoria_obj.categoria_id)
    
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


def catalogo_por_categoria(request, categoria):
    """
    Muestra productos según la categoría elegida:
    - /catalogo/perro/  → Alimento para perro
    - /catalogo/gato/   → Alimento para gato
    - /catalogo/arena/  → Arena para gato
    """

    # Relación slug → nombre real en la base de datos
    categoria_map = {
        'perro': 'Alimento para perro',
        'gato': 'Alimento para gato',
        'arena': 'Arena para gato',
    }

    nombre_categoria = categoria_map.get(categoria.lower())

    # Buscar la categoría correspondiente
    categoria_obj = Categoria.objects.filter(nombre__iexact=nombre_categoria).first()

    if categoria_obj:
        productos = Producto.objects.filter(
            categoria=categoria_obj,
            estado_producto='activo'
        ).select_related('marca')
    else:
        productos = Producto.objects.none()

    context = {
        'productos': productos,
        'categoria': nombre_categoria or categoria.capitalize(),
        'categoria_obj': categoria_obj,
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


