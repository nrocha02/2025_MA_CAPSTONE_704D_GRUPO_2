# Diagramas de Estados

Este archivo contiene los diagramas de máquinas de estados para las entidades principales del sistema.

## Estados del Pedido

```mermaid
stateDiagram-v2
    [*] --> Pendiente_Pago: Crear pedido

    Pendiente_Pago --> Pagado: Pago confirmado
    Pendiente_Pago --> Cancelado: Timeout o rechazo

    Pagado --> En_Preparacion: Iniciar preparación
    Pagado --> Cancelado: Cancelación cliente

    En_Preparacion --> Enviado: Despacho
    En_Preparacion --> Cancelado: Problema preparación

    Enviado --> En_Transito: Courier recoge

    En_Transito --> Entregado: Entrega exitosa
    En_Transito --> Devolucion: Devolución en tránsito

    Entregado --> [*]

    Devolucion --> Cancelado: Devolución procesada
    Cancelado --> [*]

    note right of Pendiente_Pago
        Estado inicial
        Timeout: 15 minutos
    end note

    note right of Pagado
        Genera documento tributario
        Descuenta stock
    end note

    note right of Enviado
        Genera código tracking
    end note
```

### Transiciones del Pedido

| Estado Origen  | Evento              | Estado Destino |
| -------------- | ------------------- | -------------- |
| [Inicial]      | Crear pedido        | Pendiente_Pago |
| Pendiente_Pago | Pago confirmado     | Pagado         |
| Pendiente_Pago | Timeout/Rechazo     | Cancelado      |
| Pagado         | Iniciar preparación | En_Preparacion |
| Pagado         | Cancelación cliente | Cancelado      |
| En_Preparacion | Despacho            | Enviado        |
| En_Preparacion | Problema            | Cancelado      |
| Enviado        | Courier recoge      | En_Transito    |
| En_Transito    | Entrega exitosa     | Entregado      |
| En_Transito    | Devolución          | Devolucion     |
| Devolucion     | Procesada           | Cancelado      |

---

## Estados del Producto

```mermaid
stateDiagram-v2
    [*] --> Activo: Crear producto

    Activo --> Inactivo: Desactivar
    Activo --> Agotado: Stock = 0
    Activo --> Descontinuado: Descontinuar

    Inactivo --> Activo: Reactivar
    Inactivo --> Descontinuado: Descontinuar

    Agotado --> Activo: Reabastecer
    Agotado --> Descontinuado: Descontinuar

    Descontinuado --> [*]

    note right of Activo
        Visible en catálogo
        Disponible para venta
    end note

    note right of Agotado
        Visible pero no comprable
        Notificación cuando disponible
    end note

    note right of Descontinuado
        No visible
        Estado final
    end note
```

### Transiciones del Producto

| Estado Origen | Evento         | Estado Destino |
| ------------- | -------------- | -------------- |
| [Inicial]     | Crear producto | Activo         |
| Activo        | Desactivar     | Inactivo       |
| Activo        | Stock = 0      | Agotado        |
| Activo        | Descontinuar   | Descontinuado  |
| Inactivo      | Reactivar      | Activo         |
| Inactivo      | Descontinuar   | Descontinuado  |
| Agotado       | Reabastecer    | Activo         |
| Agotado       | Descontinuar   | Descontinuado  |

---

## Estados de la Sesión del Carrito

```mermaid
stateDiagram-v2
    [*] --> Vacio: Nueva sesión

    Vacio --> Con_Items: Agregar producto

    Con_Items --> Con_Items: Agregar/Actualizar/Eliminar
    Con_Items --> Vacio: Eliminar todos
    Con_Items --> Checkout: Proceder al pago

    Checkout --> Vacio: Pago exitoso
    Checkout --> Con_Items: Cancelar pago

    Vacio --> [*]: Expirar sesión
    Con_Items --> [*]: Expirar sesión (24h)

    note right of Con_Items
        Session Storage
        Timeout: 24 horas
    end note
```

### Ciclo de Vida del Carrito

1. **Vacio**: Carrito recién creado o vaciado
2. **Con_Items**: Uno o más productos agregados
3. **Checkout**: Usuario en proceso de pago
4. **Expiración**: Sesión caduca después de 24 horas

### Eventos del Carrito

- **Agregar producto**: Vacio → Con_Items
- **Actualizar cantidad**: Con_Items → Con_Items
- **Eliminar producto**: Con_Items → Con_Items o Vacio
- **Proceder al pago**: Con_Items → Checkout
- **Pago exitoso**: Checkout → Vacio (limpieza)
- **Cancelar pago**: Checkout → Con_Items
- **Timeout**: Cualquier estado → [Final]

## Implementación

Los estados se implementan como:

- **Pedido**: Campo `estado` con choices en modelo Django
- **Producto**: Campo `estado` con choices en modelo Django
- **Carrito**: Lógica en clase `Carrito` basada en sesión Django
