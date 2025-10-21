# Secuencia: Búsqueda y Filtrado de Productos

Este diagrama muestra la interacción entre las capas del sistema al buscar y filtrar productos.

```mermaid
sequenceDiagram
    actor Usuario
    participant Vue as Vista (Browser)
    participant Ctrl as Controlador (View)
    participant Model as Modelo (ORM)
    participant DB as Base de Datos

    Usuario->>Vue: Selecciona filtros
    Vue->>Ctrl: GET /catalogo/?categoria=perro&marca=5

    Ctrl->>Model: Producto.objects.filter(...)
    Model->>DB: SELECT * FROM producto WHERE...
    DB-->>Model: ResultSet
    Model-->>Ctrl: QuerySet[Producto]

    Ctrl->>Model: Categoria.objects.filter(activa=True)
    Model->>DB: SELECT * FROM categoria WHERE activa=true
    DB-->>Model: ResultSet
    Model-->>Ctrl: QuerySet[Categoria]

    Ctrl->>Ctrl: Preparar contexto
    Ctrl->>Ctrl: render(template, context)
    Ctrl-->>Vue: HTML con productos filtrados
    Vue-->>Usuario: Muestra resultados
```

## Patrón MVC en Django

- **Vista (Browser)**: Interfaz de usuario
- **Controlador (View)**: Lógica de negocio en Django
- **Modelo (ORM)**: Abstracción de base de datos

## Queries Ejecutados

1. **Productos filtrados**: Con JOIN a categoría y marca
2. **Categorías activas**: Para mostrar en sidebar
3. **Marcas activas**: Para filtros adicionales
