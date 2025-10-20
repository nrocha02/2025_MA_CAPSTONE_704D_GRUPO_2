# Secuencia: Actualización de Cantidad en Carrito

Este diagrama muestra el flujo detallado de actualización de cantidad de un producto en el carrito.

```mermaid
sequenceDiagram
    actor Usuario
    participant JS as JavaScript
    participant View as Vista Django
    participant Carrito as Clase Carrito
    participant Session as Django Session

    Usuario->>JS: Cambia cantidad
    JS->>View: POST /carrito/actualizar/
    Note over JS,View: {producto_id: 5, cantidad: 3}

    View->>Carrito: Carrito(request)
    Carrito->>Session: request.session.get('carrito')
    Session-->>Carrito: carrito_dict

    View->>Carrito: actualizar_cantidad(5, 3)
    Carrito->>Carrito: carrito[5]['cantidad'] = 3
    Carrito->>Carrito: calcular subtotal
    Carrito->>Session: request.session['carrito'] = carrito_dict
    Carrito->>Session: request.session.modified = True

    View->>Carrito: get_total_productos()
    Carrito-->>View: total_items
    View->>Carrito: get_subtotal()
    Carrito-->>View: subtotal
    View->>Carrito: get_total()
    Carrito-->>View: total

    View-->>JS: JSON response
    JS->>JS: Actualizar UI
    JS-->>Usuario: Muestra nuevos totales
```

## Clase Carrito

La clase `Carrito` encapsula toda la lógica de gestión del carrito:

- **Inicialización**: Lee carrito de sesión
- **Operaciones**: Agregar, actualizar, eliminar
- **Cálculos**: Subtotales, total, envío
- **Persistencia**: Guarda cambios en sesión

## Almacenamiento en Sesión

```python
# Estructura del carrito en sesión
carrito = {
    "5": {
        "producto_id": 5,
        "nombre": "Alimento Royal Canin",
        "precio": 45990,
        "cantidad": 3,
        "imagen": "productos/royal-canin.jpg"
    },
    "12": {
        "producto_id": 12,
        "nombre": "Arena Sanitaria",
        "precio": 8990,
        "cantidad": 2,
        "imagen": "productos/arena.jpg"
    }
}
```
