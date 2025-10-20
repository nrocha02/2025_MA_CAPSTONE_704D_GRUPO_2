# Flujo de Navegación del Catálogo

Este diagrama de secuencia muestra el proceso completo cuando un usuario navega por el catálogo de productos.

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant Django
    participant DB
    participant Spaces

    Usuario->>Browser: Accede al catálogo
    Browser->>Django: GET /catalogo/
    Django->>DB: SELECT productos WHERE estado='activo'
    DB-->>Django: Lista de productos
    Django->>Django: Aplicar filtros (categoría, marca)
    Django->>Django: Renderizar template
    Django-->>Browser: HTML + URLs de imágenes
    Browser->>Spaces: GET imagen1.jpg
    Spaces-->>Browser: Imagen
    Browser->>Spaces: GET imagen2.jpg
    Spaces-->>Browser: Imagen
    Browser-->>Usuario: Muestra catálogo
```

## Puntos Clave

1. **Consulta a Base de Datos**: Se filtran solo productos activos
2. **Filtrado Dinámico**: Categoría y marca se aplican en el servidor
3. **Carga de Imágenes**: Las imágenes se cargan desde DigitalOcean Spaces
4. **Renderizado**: El template se renderiza en el servidor (SSR)
5. **Performance**: Las imágenes se cargan en paralelo desde el CDN
