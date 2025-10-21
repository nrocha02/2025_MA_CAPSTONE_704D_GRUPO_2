# Diagramas de Módulos Django

## 1. Módulo `pets` (Proyecto Principal)

Configuración global y enrutamiento principal.

```mermaid
graph LR
    A[pets/] --> B[settings.py]
    A --> C[urls.py]
    A --> D[wsgi.py]
    A --> E[asgi.py]

    B --> F[Configuración BD]
    B --> G[Apps Instaladas]
    B --> H[Middleware]
    B --> I[Templates]
    B --> J[Static Files]
    B --> K[DO Spaces Config]
```

---

## 2. Módulo `ventas`

Catálogo público y gestión de productos.

```mermaid
graph TB
    subgraph "ventas"
        A[models.py] --> B[Producto]
        A --> C[Categoria]
        A --> D[Marca]
        A --> E[Pedido]
        A --> F[Cliente*]
        A --> G[Pago]

        H[views.py] --> I[index]
        H --> J[catalogo]
        H --> K[producto]

        L[urls.py] --> H

        M[templatetags/] --> N[image_tags.py]

        O[templates/] --> P[index.html]
        O --> Q[catalogo.html]
        O --> R[producto.html]
        O --> S[ventas_base.html]
    end
```

---

## 3. Módulo `carrito`

Gestión del carrito de compras en sesión.

```mermaid
graph TB
    subgraph "carrito"
        A[carrito.py] --> B[Clase Carrito]

        B --> C[agregar]
        B --> D[eliminar]
        B --> E[actualizar_cantidad]
        B --> F[get_productos]
        B --> G[get_total]
        B --> H[limpiar]

        I[views.py] --> J[ver_carrito]
        I --> K[agregar_carrito]
        I --> L[eliminar_carrito]
        I --> M[actualizar_carrito]

        N[context_processors.py] --> O[carrito global]

        P[urls.py] --> I
    end
```

---

## 4. Módulo `dashboard`

Panel administrativo para gestión.

```mermaid
graph TB
    subgraph "dashboard"
        A[views.py] --> B[admin_dashboard]
        A --> C[Categorías CRUD]
        A --> D[Productos CRUD]

        E[storage.py] --> F[upload_product_image]
        E --> G[delete_product_image]
        E --> H[is_spaces_configured]

        I[urls.py] --> A

        J[templates/] --> K[base_dashboard.html]
        J --> L[admin/dashboard.html]
        J --> M[categoria/]
        J --> N[producto/]
    end
```

**Funcionalidades:**

- CRUD completo de productos
- CRUD completo de categorías
- Integración con DigitalOcean Spaces
- Upload y eliminación de imágenes
- Paginación de listados
- Filtros y búsqueda
