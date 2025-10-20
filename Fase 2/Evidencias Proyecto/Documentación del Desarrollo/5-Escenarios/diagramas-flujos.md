# Flujos de Trabajo Principales

Este archivo contiene diagramas de flujo para los principales procesos del sistema.

## Flujo: Navegar Catálogo

```mermaid
flowchart TD
    Start([Inicio]) --> A[Usuario accede al sitio]
    A --> B{¿Categoría específica?}
    B -->|Sí| C[Filtrar por categoría]
    B -->|No| D[Mostrar todos los productos]
    C --> E[Cargar productos filtrados]
    D --> E
    E --> F{¿Aplicar más filtros?}
    F -->|Marca| G[Filtrar por marca]
    F -->|Búsqueda| H[Buscar por texto]
    F -->|No| I[Mostrar resultados]
    G --> I
    H --> I
    I --> J{¿Productos encontrados?}
    J -->|Sí| K[Renderizar catálogo]
    J -->|No| L[Mostrar mensaje "Sin resultados"]
    K --> M[Cargar imágenes desde Spaces]
    L --> End([Fin])
    M --> N{¿Ver detalle?}
    N -->|Sí| O[Ir a página de producto]
    N -->|No| End
    O --> End
```

---

## Flujo: Realizar Compra

```mermaid
flowchart TD
    Start([Inicio: Carrito con items]) --> A{¿Usuario registrado?}

    A -->|Sí| B[Cargar datos guardados]
    A -->|No| C[Formulario invitado]

    B --> D[Mostrar direcciones guardadas]
    C --> E[Solicitar datos de envío]
    D --> F{¿Nueva dirección?}
    F -->|Sí| E
    F -->|No| G[Seleccionar dirección]

    E --> H[Validar datos]
    G --> H

    H --> I{¿Datos válidos?}
    I -->|No| J[Mostrar errores]
    J --> E

    I -->|Sí| K[BEGIN TRANSACTION]
    K --> L{¿Tipo cliente?}

    L -->|Invitado| M[INSERT sesion_invitado]
    L -->|Registrado| N[SELECT cliente_persona]
    L -->|Empresa| O[SELECT cliente_empresa]

    M --> P[INSERT pedido]
    N --> P
    O --> P

    P --> Q[Loop: Para cada item]
    Q --> R[Verificar stock con lock]
    R --> S{¿Stock suficiente?}

    S -->|No| T[ROLLBACK]
    T --> U[Error: Stock insuficiente]
    U --> End([Fin])

    S -->|Sí| V[INSERT pedido_item]
    V --> W[UPDATE stock]
    W --> X[INSERT movimiento_stock]
    X --> Y{¿Más items?}

    Y -->|Sí| Q
    Y -->|No| Z[Iniciar pago Transbank]

    Z --> AA[INSERT pago pendiente]
    AA --> AB[COMMIT TRANSACTION]
    AB --> AC[Redirect a Transbank]
    AC --> AD{¿Resultado pago?}

    AD -->|Aprobado| AE[UPDATE pago aprobado]
    AD -->|Rechazado| AF[UPDATE pago rechazado]

    AE --> AG[UPDATE pedido Pagado]
    AF --> AH[UPDATE pedido Cancelado]

    AG --> AI[INSERT pedido_registro]
    AH --> AJ[Revertir stock]

    AI --> AK{¿Tipo documento?}
    AK -->|Persona| AL[INSERT boleta]
    AK -->|Empresa| AM[INSERT factura]

    AL --> AN[Limpiar carrito]
    AM --> AN
    AJ --> AN

    AN --> AO[Mostrar confirmación]
    AO --> End
```

---

## Flujo: Gestión de Producto (Dashboard)

```mermaid
flowchart TD
    Start([Admin en Dashboard]) --> A{¿Acción?}

    A -->|Crear| B[Click "Nuevo Producto"]
    A -->|Editar| C[Click "Editar"]
    A -->|Eliminar| D[Click "Eliminar"]
    A -->|Listar| E[Ver lista de productos]

    B --> F[Formulario vacío]
    C --> G[Formulario con datos]

    F --> H[Admin completa datos]
    G --> H

    H --> I{¿Tiene imagen?}
    I -->|Sí| J[Upload a Spaces]
    I -->|No| K[Validar datos]
    J --> K

    K --> L{¿Válido?}
    L -->|No| M[Mostrar errores]
    M --> H

    L -->|Sí| N[Guardar en BD]
    N --> O[Registrar movimiento stock]
    O --> P[Redirect a lista]

    D --> Q[Confirmar eliminación]
    Q --> R{¿Confirma?}
    R -->|No| E
    R -->|Sí| S{¿Tiene pedidos?}
    S -->|Sí| T[Error: No se puede eliminar]
    S -->|No| U[Eliminar imagen de Spaces]
    U --> V[DELETE de BD]
    V --> P
    T --> E

    E --> End([Fin])
    P --> End
```

---

## Flujo: Manejo de Errores en Checkout

```mermaid
flowchart TD
    Start([Inicio Checkout]) --> A[Validar carrito]
    A --> B{¿Carrito vacío?}
    B -->|Sí| C[Error: Carrito vacío]
    C --> End([Fin])

    B -->|No| D[Validar formulario]
    D --> E{¿Datos válidos?}
    E -->|No| F[Mostrar errores de validación]
    F --> End

    E -->|Sí| G[BEGIN TRANSACTION]
    G --> H[Verificar stock con locks]
    H --> I{¿Stock disponible?}
    I -->|No| J[ROLLBACK]
    J --> K[Error: Stock insuficiente]
    K --> End

    I -->|Sí| L[Crear pedido]
    L --> M[Actualizar stock]
    M --> N[Iniciar pago]
    N --> O{¿Transbank disponible?}
    O -->|No| P[ROLLBACK]
    P --> Q[Error: Servicio de pago no disponible]
    Q --> End

    O -->|Sí| R[COMMIT]
    R --> S[Redirect a Transbank]
    S --> T[Usuario paga]
    T --> U{¿Pago exitoso?}
    U -->|No| V[Revertir stock]
    V --> W[Cancelar pedido]
    W --> X[Mostrar error de pago]
    X --> End

    U -->|Sí| Y[Confirmar pedido]
    Y --> Z[Generar documento]
    Z --> AA[Limpiar carrito]
    AA --> AB[Mostrar confirmación]
    AB --> End
```

## Puntos de Decision Críticos

### 1. Validación de Stock

- **Momento**: Antes de confirmar pedido
- **Método**: SELECT FOR UPDATE (row lock)
- **Fallback**: Mostrar error, preservar carrito

### 2. Procesamiento de Pago

- **Timeout**: 15 minutos
- **Retry**: No automático (requiere acción del usuario)
- **Rollback**: Reversión completa de transacción

### 3. Upload de Imágenes

- **Validación**: Tipo MIME, tamaño máximo
- **Fallback**: Producto sin imagen (placeholder)
- **Rollback**: Si falla INSERT en BD, eliminar de Spaces

## Tiempos Estimados

| Flujo            | Tiempo Promedio | Tiempo Máximo |
| ---------------- | --------------- | ------------- |
| Navegar catálogo | 30 segundos     | 2 minutos     |
| Realizar compra  | 5 minutos       | 15 minutos    |
| Gestión producto | 2 minutos       | 5 minutos     |
