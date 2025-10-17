from django.shortcuts import render, get_object_or_404
from .carrito import Carrito
from apps.ventas.models import Producto
from django.http import JsonResponse

def ver_carrito(request):
    carrito = Carrito(request)
    productos_carrito = carrito.get_productos()
    subtotal = carrito.get_subtotal()
    costo_envio = 2990
    total = carrito.get_total(costo_envio)
    
    context = {
        "productos_carrito": productos_carrito,
        "subtotal": subtotal,
        "costo_envio": costo_envio,
        "total": total,
        "carrito_vacio": len(productos_carrito) == 0
    }
    return render(request, "carrito/ver_carrito.html", context)

def agregar_carrito(request):
    carrito = Carrito(request)
    if request.POST.get("action") == "post":
        producto_id = int(request.POST.get("producto_id"))
        cantidad = int(request.POST.get("cantidad", 1))
        producto = get_object_or_404(Producto, producto_id=producto_id)
        carrito.agregar(producto=producto, cantidad=cantidad)
        return JsonResponse({
            "success": True,
            "nombre_producto": producto.nombre,
            "total_productos": carrito.get_total_productos()
        })

def eliminar_carrito(request):
    carrito = Carrito(request)
    if request.POST.get("action") == "post":
        producto_id = request.POST.get("producto_id")
        carrito.eliminar(producto_id)
        return JsonResponse({
            "success": True,
            "total_productos": carrito.get_total_productos(),
            "subtotal": carrito.get_subtotal(),
            "total": carrito.get_total()
        })

def actualizar_carrito(request):
    carrito = Carrito(request)
    if request.POST.get("action") == "post":
        producto_id = request.POST.get("producto_id")
        cantidad = int(request.POST.get("cantidad"))
        carrito.actualizar_cantidad(producto_id, cantidad)
        return JsonResponse({
            "success": True,
            "total_productos": carrito.get_total_productos(),
            "subtotal": carrito.get_subtotal(),
            "total": carrito.get_total()
        })