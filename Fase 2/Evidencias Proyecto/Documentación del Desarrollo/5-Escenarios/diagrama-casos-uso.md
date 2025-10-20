# Diagrama General de Casos de Uso

Este diagrama muestra todos los casos de uso principales del sistema y su relación con los actores.

```mermaid
graph TB
    subgraph "Sistema Cordillera Pets"
        UC1[UC-01: Navegar Catálogo]
        UC2[UC-02: Buscar Productos]
        UC3[UC-03: Ver Detalle Producto]
        UC4[UC-04: Gestionar Carrito]
        UC5[UC-05: Realizar Compra]
        UC6[UC-06: Procesar Pago]
        UC7[UC-07: Gestionar Productos]
        UC8[UC-08: Gestionar Categorías]
        UC9[UC-09: Subir Imágenes]
        UC10[UC-10: Ver Dashboard]
    end

    Cliente[Cliente Anónimo] --> UC1
    Cliente --> UC2
    Cliente --> UC3
    Cliente --> UC4
    Cliente --> UC5

    ClienteReg[Cliente Registrado] --> UC5

    Admin[Administrador] --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10

    UC5 ..> UC6: include
    UC7 ..> UC9: include

    Transbank[Transbank] --> UC6
    Spaces[DO Spaces] --> UC9
```

## Catálogo de Casos de Uso

### Módulo: Ventas (Frontend)

| ID    | Nombre               | Actor                      | Descripción                                         |
| ----- | -------------------- | -------------------------- | --------------------------------------------------- |
| UC-01 | Navegar Catálogo     | Cliente Anónimo            | Explorar productos por categorías                   |
| UC-02 | Buscar Productos     | Cliente Anónimo            | Buscar productos por nombre, marca                  |
| UC-03 | Ver Detalle Producto | Cliente Anónimo            | Ver información completa del producto               |
| UC-04 | Gestionar Carrito    | Cliente Anónimo            | Agregar, actualizar, eliminar productos del carrito |
| UC-05 | Realizar Compra      | Cliente Anónimo/Registrado | Completar proceso de checkout                       |
| UC-06 | Procesar Pago        | Sistema Transbank          | Procesar pago con tarjeta                           |

### Módulo: Dashboard (Backend)

| ID    | Nombre               | Actor               | Descripción                        |
| ----- | -------------------- | ------------------- | ---------------------------------- |
| UC-07 | Gestionar Productos  | Administrador       | CRUD de productos                  |
| UC-08 | Gestionar Categorías | Administrador       | CRUD de categorías                 |
| UC-09 | Subir Imágenes       | DigitalOcean Spaces | Upload de imágenes a cloud storage |
| UC-10 | Ver Dashboard        | Administrador       | Ver métricas y estadísticas        |

## Relaciones entre Casos de Uso

### Include (<<include>>)

Relación de dependencia obligatoria:

- **UC-05 include UC-06**: Realizar Compra siempre incluye Procesar Pago
- **UC-07 include UC-09**: Gestionar Productos incluye Subir Imágenes (si se proporciona imagen)

### Extend (<<extend>>)

Relación de extensión opcional:

- **UC-05 extend Autenticación**: Si el usuario decide registrarse durante el checkout

### Herencia (Generalización)

Especialización de casos de uso:

- **UC-05**: Tiene variantes para cliente anónimo y cliente registrado

## Prioridad de Casos de Uso

### Alta Prioridad (Críticos)

- UC-05: Realizar Compra
- UC-06: Procesar Pago
- UC-01: Navegar Catálogo
- UC-04: Gestionar Carrito

### Media Prioridad (Importantes)

- UC-07: Gestionar Productos
- UC-03: Ver Detalle Producto
- UC-02: Buscar Productos

### Baja Prioridad (Opcionales)

- UC-08: Gestionar Categorías
- UC-10: Ver Dashboard

## Complejidad de Implementación

| Caso de Uso | Complejidad | Esfuerzo (días) |
| ----------- | ----------- | --------------- |
| UC-01       | Media       | 3               |
| UC-02       | Baja        | 2               |
| UC-03       | Baja        | 2               |
| UC-04       | Media       | 4               |
| UC-05       | Alta        | 8               |
| UC-06       | Alta        | 5               |
| UC-07       | Media       | 5               |
| UC-08       | Baja        | 2               |
| UC-09       | Media       | 3               |
| UC-10       | Media       | 3               |

**Total estimado**: 37 días de desarrollo
