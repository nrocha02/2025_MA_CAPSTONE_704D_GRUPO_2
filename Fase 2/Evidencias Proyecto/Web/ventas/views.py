from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, ItemCarrito

from .models import *

def index(request):
    return render(request, 'ventas/index.html')
    
def producto(request):
    return render(request, 'ventas/producto.html')

def catalogo(request):
    return render(request, 'ventas/catalogo.html')

def carrito(request):
    return render(request, 'ventas/carrito.html')

def perro(request):
    return render(request, 'ventas/perro.html')

def gato(request):
    return render(request, 'ventas/gato.html')

def arena(request):
    return render(request, 'ventas/arena.html')



##Carrito##

