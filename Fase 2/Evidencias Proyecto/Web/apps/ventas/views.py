import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as login_aut
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from .models import *

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

def iniciosesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Email o RUT
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}!')
            return redirect ('index')
        else:
            print(messages.error(request, 'Usuario o Contraseña Incorrecta'))

    return render(request, 'ventas/iniciosesion.html')

def registro_view(request):
    """Vista para registro de nuevos clientes"""
    if request.method == 'POST':

        rut = request.POST.get('rut')
        nombres = request.POST.get('nombres')
        apellido_paterno = request.POST.get('apellido_paterno')
        apellido_materno = request.POST.get('apellido_materno')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        password = request.POST.get('password')

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if ClientePersona.objects.filter(rut=rut).exists():
            messages.error(request, 'Ya existe un cliente con este RUT.')
        elif ClientePersona.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe un cliente con este email.')
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
                    password=password_hash
                )

                messages.success(request, 'Cliente registrado exitosamente. Ya puede iniciar sesión.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f'Error al registrar cliente: {str(e)}')

    return render(request, 'ventas/registro.html')