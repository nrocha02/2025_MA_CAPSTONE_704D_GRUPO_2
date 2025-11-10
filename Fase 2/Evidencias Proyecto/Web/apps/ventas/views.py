import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as login_aut
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .brevo_service import BrevoEmailService
# Configurar logger
logger = logging.getLogger(__name__)




def index(request):
    # Obtener productos recomendados (los primeros 8 productos activos)
    productos_recomendados = Producto.objects.filter(
        estado_producto='activo'
    ).select_related('categoria', 'marca')[:8]
    
    # Obtener todas las marcas activas para mostrar en el carrusel
    marcas = Marca.objects.filter(activa=True)
    
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
    categoria_slug = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    
    # Filtrar por slug de categoría
    if categoria_slug:
        categoria_obj = Categoria.objects.filter(slug=categoria_slug, activa=True).first()
        if categoria_obj:
            productos = productos.filter(categoria=categoria_obj)
    
    if marca_id:
        productos = productos.filter(marca_id=marca_id)
    
    # Obtener todas las categorías y marcas para los filtros
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'categoria_seleccionada': categoria_slug,
        'marca_seleccionada': marca_id,
    }
    return render(request, 'ventas/catalogo.html', context)

def iniciosesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Email o RUT
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}! Has iniciado sesión correctamente.')
            return redirect ('index')
        else:
            messages.error(request, 'Usuario o Contraseña Incorrecta')

    return render(request, 'ventas/iniciosesion.html')

def logout_view(request):
    #Vista para cerrar sesión"""
    login_aut(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('index')

def registro_view(request):
    #Vista para registro de nuevos clientes"""
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

                try:
                    brevo_service = BrevoEmailService()
                    email_result = brevo_service.send_welcome_email(
                        cliente_email=email,
                        cliente_nombre=f"{nombres} {apellido_paterno}"
                    )

                    if email_result['success']:
                        logger.info(f"Email de bienvenida enviado a {email}")
                        messages.success(request, 'Cliente registrado exitosamente. Se ha enviado un correo de bienvenida. Ya puede iniciar sesión.')
                    else:
                        logger.warning(f"No se pudo enviar email de bienvenida: {email_result['message']}")
                        messages.success(request, 'Cliente registrado exitosamente. Ya puede iniciar sesión.')
                        messages.warning(request, 'No se pudo enviar el correo de bienvenida.')

                except Exception as e:
                    logger.error(f"Error al enviar email de bienvenida: {e}")
                    messages.success(request, 'Cliente registrado exitosamente. Ya puede iniciar sesión.')
                    messages.warning(request, 'No se pudo enviar el correo de bienvenida.')
                return redirect('iniciosesion')

            except Exception as e:
                messages.error(request, f'Error al registrar cliente: {str(e)}')

    return render(request, 'ventas/registro.html')

