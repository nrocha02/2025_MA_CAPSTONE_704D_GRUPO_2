from apps.ventas.models import Producto

class Carrito():
    def __init__(self, request):
        self.session = request.session

        # Obtener la llave de la sesión
        carrito = self.session.get("session_key")

        # Si no existe, crear un carrito vacío
        if 'session_key' not in request.session:
            carrito = self.session['session_key'] = {}

        # Verificar si el carrito existe en todos los pages
        self.carrito = carrito
        
    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.producto_id)

        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += cantidad
        else:
            self.carrito[producto_id] = {
                "precio": str(producto.precio),
                "cantidad": cantidad,
                "nombre": producto.nombre,
                "imagen_url": producto.imagen_url or ""
            }
        self.session.modified = True

    def eliminar(self, producto_id):
        producto_id = str(producto_id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.session.modified = True

    def actualizar_cantidad(self, producto_id, cantidad):
        producto_id = str(producto_id)
        if producto_id in self.carrito:
            if cantidad <= 0:
                self.eliminar(producto_id)
            else:
                self.carrito[producto_id]['cantidad'] = cantidad
                self.session.modified = True

    def get_productos(self):
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(producto_id__in=producto_ids)
        
        # Añadir información del carrito a cada producto
        for producto in productos:
            producto_id = str(producto.producto_id)
            if producto_id in self.carrito:
                # Verificar si existe la clave 'cantidad', si no, asignar 1 por defecto
                producto.cantidad_carrito = self.carrito[producto_id].get('cantidad', 1)
                
                # Actualizar el carrito si no tenía cantidad (para compatibilidad hacia atrás)
                if 'cantidad' not in self.carrito[producto_id]:
                    self.carrito[producto_id]['cantidad'] = 1
                    self.carrito[producto_id]['nombre'] = producto.nombre
                    self.carrito[producto_id]['imagen_url'] = producto.imagen_url or ""
                    self.session.modified = True
                
                producto.subtotal = int(self.carrito[producto_id]['precio']) * producto.cantidad_carrito
        
        return productos

    def get_total_productos(self):
        return sum(item.get('cantidad', 1) for item in self.carrito.values())

    def get_subtotal(self):
        return sum(int(item['precio']) * item.get('cantidad', 1) for item in self.carrito.values())

    def get_total(self, costo_envio=2990):
        return self.get_subtotal() + costo_envio

    def limpiar(self):
        self.carrito = {}
        self.session['session_key'] = {}
        self.session.modified = True