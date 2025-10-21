# Flujo de Gestión del Carrito

Este diagrama muestra el proceso de agregar productos al carrito con verificación de stock.

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant Django
    participant Session
    participant DB

    Usuario->>Browser: Click "Agregar al carrito"
    Browser->>Django: POST /carrito/agregar/
    Note over Browser,Django: AJAX Request

    Django->>Session: Obtener carrito actual
    Session-->>Django: Datos del carrito (dict)

    Django->>DB: Verificar stock del producto
    DB-->>Django: Producto con stock

    alt Stock disponible
        Django->>Django: Agregar/actualizar producto en carrito
        Django->>Session: Guardar carrito actualizado
        Session-->>Django: OK
        Django-->>Browser: JSON {success: true, total: X}
        Browser->>Browser: Actualizar contador carrito
        Browser-->>Usuario: Muestra confirmación
    else Sin stock
        Django-->>Browser: JSON {success: false, error: "Sin stock"}
        Browser-->>Usuario: Muestra error
    end
```

## Características

- **AJAX**: Request asíncrono sin recargar la página
- **Session Storage**: Carrito almacenado en sesión Django
- **Validación de Stock**: Verificación en tiempo real
- **Respuesta JSON**: Comunicación ligera entre frontend y backend
- **UX Optimizada**: Actualización inmediata del contador
