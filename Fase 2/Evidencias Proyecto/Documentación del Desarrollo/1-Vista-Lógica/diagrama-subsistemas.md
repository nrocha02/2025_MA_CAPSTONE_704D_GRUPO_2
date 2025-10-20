# Diagramas de Subsistemas Funcionales

## 1. Subsistema de Gestión de Productos

```mermaid
graph LR
    A[Dashboard Admin] --> B[Gestión Productos]
    B --> C[CRUD Productos]
    B --> D[CRUD Categorías]
    B --> E[Upload Imágenes]
    C --> F[(Base de Datos)]
    D --> F
    E --> G[DigitalOcean Spaces]
```

---

## 2. Subsistema de Ventas

```mermaid
graph LR
    A[Usuario Web] --> B[Catálogo]
    B --> C[Filtros]
    B --> D[Búsqueda]
    C --> E[Vista Productos]
    D --> E
    E --> F[Detalle Producto]
```

---

## 3. Subsistema de Carrito

```mermaid
graph LR
    A[Agregar Producto] --> B[Carrito Session]
    C[Actualizar Cantidad] --> B
    D[Eliminar Producto] --> B
    B --> E[Calcular Total]
    E --> F[Mostrar Carrito]
    F --> G[Proceder al Checkout]
```

---

## 4. Subsistema de Pedidos - Estados

```mermaid
stateDiagram-v2
    [*] --> Pendiente_Pago
    Pendiente_Pago --> Pagado
    Pagado --> En_Preparacion
    En_Preparacion --> Enviado
    Enviado --> Entregado
    Entregado --> [*]

    Pendiente_Pago --> Cancelado
    Pagado --> Cancelado
    Cancelado --> [*]
```

---

## 5. Subsistema de Clientes

```mermaid
graph TB
    A[Cliente] --> B{Tipo}
    B -->|Registrado| C[ClientePersona]
    B -->|Corporativo| D[ClienteEmpresa]
    B -->|Sin Registro| E[SesionInvitado]

    C --> F[Direcciones]
    C --> G[Métodos de Pago]
    D --> F
    D --> G
```
