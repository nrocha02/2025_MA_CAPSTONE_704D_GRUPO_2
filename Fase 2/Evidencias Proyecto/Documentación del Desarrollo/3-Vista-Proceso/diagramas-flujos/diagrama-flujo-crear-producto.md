# Flujo de Creación de Producto (Dashboard)

Este diagrama muestra el proceso completo de creación de un producto por un administrador, incluyendo la subida de imágenes a DigitalOcean Spaces.

```mermaid
sequenceDiagram
    actor Admin
    participant Browser
    participant Django
    participant Spaces
    participant DB

    Admin->>Browser: Completa formulario producto
    Browser->>Django: POST /dashboard/producto/crear/
    Note over Browser,Django: Multipart Form Data

    Django->>Django: Validar datos

    alt Con imagen
        Django->>Django: Generar slug desde nombre
        Django->>Spaces: PUT productos/{slug}.jpg
        Note over Django,Spaces: boto3 upload_fileobj
        Spaces-->>Django: URL de la imagen
        Django->>Django: Guardar ruta relativa
    end

    Django->>DB: INSERT INTO producto
    DB-->>Django: producto_id generado

    Django->>DB: INSERT INTO movimiento_stock
    DB-->>Django: Registro creado

    Django-->>Browser: Redirect a lista de productos
    Browser-->>Admin: Muestra mensaje de éxito
```

## Proceso de Upload

1. **Validación**: Datos del formulario son validados
2. **Generación de Slug**: Nombre único basado en el nombre del producto
3. **Upload a Spaces**: Imagen subida vía boto3 SDK (S3-compatible)
4. **Inserción en BD**: Producto creado con referencia a la imagen
5. **Movimiento de Stock**: Registro inicial del inventario
6. **Confirmación**: Redirect con mensaje de éxito
