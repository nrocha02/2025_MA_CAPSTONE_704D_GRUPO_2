# Escenario: Gestión de Productos por Administrador

Este diagrama muestra el flujo completo de gestión de productos desde el dashboard administrativo.

```mermaid
sequenceDiagram
    actor Admin
    participant Browser
    participant Django
    participant DB
    participant Spaces

    Note over Admin,Spaces: Fase 1: Acceso al Dashboard
    Admin->>Browser: Accede a /dashboard/
    Browser->>Django: GET /dashboard/
    Note over Browser,Django: Requiere autenticación
    Django->>DB: SELECT estadísticas (productos, stock bajo, etc.)
    DB-->>Django: Datos agregados
    Django-->>Browser: dashboard.html con métricas
    Browser-->>Admin: Muestra panel principal

    Note over Admin,Spaces: Fase 2: Crear Nuevo Producto
    Admin->>Browser: Click "Nuevo Producto"
    Browser->>Django: GET /dashboard/producto/crear/
    Django->>DB: SELECT categorías activas
    Django->>DB: SELECT marcas activas
    DB-->>Django: Listas de opciones
    Django-->>Browser: form.html con selects
    Browser-->>Admin: Muestra formulario

    Admin->>Browser: Completa formulario
    Note over Admin: Nombre: Alimento Royal Canin Adulto<br/>SKU: RC-ADULTO-15KG<br/>Precio: 45990<br/>Stock: 50<br/>Categoría: Alimento Perro<br/>Marca: Royal Canin<br/>Imagen: royal-canin-adulto.jpg

    Browser->>Django: POST /dashboard/producto/crear/
    Note over Browser,Django: Multipart form data

    Django->>Django: Validar datos
    Django->>Django: Generar slug: "alimento-royal-canin-adulto"

    Note over Admin,Spaces: Fase 3: Upload de Imagen
    Django->>Django: Leer archivo imagen (2.3 MB)
    Django->>Django: Validar tipo (JPEG) y tamaño

    Django->>Spaces: PUT productos/alimento-royal-canin-adulto.jpg
    Note over Django,Spaces: boto3 S3 API<br/>Headers: Content-Type, ACL=public-read
    Spaces->>Spaces: Almacenar imagen
    Spaces-->>Django: URL: productos/alimento-royal-canin-adulto.jpg

    Note over Admin,Spaces: Fase 4: Guardar en Base de Datos
    Django->>DB: INSERT INTO producto
    Note over Django,DB: producto_id, categoria_id, marca_id,<br/>sku, nombre, precio, stock,<br/>imagen_url, slug, estado='activo'
    DB-->>Django: producto_id = 127

    Django->>DB: INSERT INTO movimiento_stock
    Note over Django,DB: tipo='ingreso', cantidad=50
    DB-->>Django: Registro creado

    Django-->>Browser: Redirect a /dashboard/producto/
    Browser->>Browser: Mostrar mensaje: "Producto creado exitosamente"
    Browser-->>Admin: Lista de productos actualizada

    Note over Admin,Spaces: Fase 5: Editar Producto
    Admin->>Browser: Click "Editar" en producto 127
    Browser->>Django: GET /dashboard/producto/127/editar/
    Django->>DB: SELECT producto WHERE id=127
    DB-->>Django: Datos del producto
    Django-->>Browser: form.html con datos precargados
    Browser-->>Admin: Muestra formulario

    Admin->>Browser: Cambia precio a 42990
    Admin->>Browser: Sube nueva imagen
    Browser->>Django: POST /dashboard/producto/127/editar/

    Django->>Django: Detectar cambio de imagen
    Django->>Spaces: Guardar imagen anterior: royal-canin-adulto.jpg

    Django->>Spaces: PUT productos/alimento-royal-canin-adulto.jpg
    Note over Django,Spaces: Reemplazar imagen existente
    Spaces-->>Django: OK

    Django->>DB: UPDATE producto SET precio=42990
    DB-->>Django: OK

    Django-->>Browser: Redirect con mensaje éxito
    Browser-->>Admin: Producto actualizado

    Note over Admin,Spaces: Fase 6: Eliminar Producto
    Admin->>Browser: Click "Eliminar" en producto antiguo
    Browser->>Django: GET /dashboard/producto/99/eliminar/
    Django->>DB: SELECT producto WHERE id=99
    DB-->>Django: Producto con imagen_url
    Django-->>Browser: delete.html con confirmación
    Browser-->>Admin: Solicita confirmación

    Admin->>Browser: Confirma eliminación
    Browser->>Django: POST /dashboard/producto/99/eliminar/

    Django->>DB: DELETE FROM producto WHERE id=99
    DB-->>Django: OK (CASCADE elimina movimientos)

    Django->>Spaces: DELETE productos/producto-antiguo.jpg
    Spaces-->>Django: OK

    Django-->>Browser: Redirect con mensaje
    Browser-->>Admin: Producto eliminado exitosamente
```

## Operaciones CRUD Detalladas

### CREATE (Crear Producto)

**Precondiciones:**

- Administrador autenticado
- Categorías y marcas existen en BD
- Imagen válida (JPEG, PNG, < 5 MB)

**Proceso:**

1. Validar campos obligatorios (nombre, precio, SKU, stock)
2. Verificar SKU único
3. Generar slug desde nombre (lowercase, hyphens)
4. Subir imagen a DigitalOcean Spaces
5. Insertar producto en BD
6. Registrar movimiento de stock inicial

**Postcondiciones:**

- Producto creado con estado 'activo'
- Imagen disponible en CDN
- Movimiento de stock tipo 'ingreso'
- Producto visible en catálogo

**Validaciones:**

```python
# Validación de formulario
if not nombre or len(nombre) < 3:
    error = "Nombre debe tener al menos 3 caracteres"

if precio <= 0:
    error = "Precio debe ser mayor a 0"

if Producto.objects.filter(sku=sku).exists():
    error = "SKU ya existe"

if imagen and imagen.size > 5 * 1024 * 1024:  # 5 MB
    error = "Imagen muy grande"
```

---

### READ (Leer Productos)

**Listado con Paginación:**

```python
productos = Producto.objects.select_related('categoria', 'marca') \
    .filter(estado='activo') \
    .order_by('-fecha_creacion')

paginator = Paginator(productos, 20)  # 20 por página
page = paginator.get_page(page_number)
```

**Filtros Disponibles:**

- Categoría
- Marca
- Estado (activo, inactivo, agotado)
- Búsqueda por nombre/SKU

**Métricas del Dashboard:**

```python
stats = {
    'total_productos': Producto.objects.count(),
    'stock_bajo': Producto.objects.filter(stock__lt=10).count(),
    'productos_activos': Producto.objects.filter(estado='activo').count(),
    'valor_inventario': Producto.objects.aggregate(
        total=Sum(F('stock') * F('precio'))
    )['total']
}
```

---

### UPDATE (Actualizar Producto)

**Campos Editables:**

- Nombre
- Descripción
- Precio
- Stock (con registro de movimiento)
- Categoría
- Marca
- Estado
- Imagen

**Manejo de Imagen:**

```python
if nueva_imagen:
    # Eliminar imagen anterior de Spaces
    if producto.imagen:
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=producto.imagen
        )

    # Subir nueva imagen
    s3_client.upload_fileobj(
        nueva_imagen,
        bucket_name,
        f'productos/{slug}.jpg',
        ExtraArgs={'ACL': 'public-read'}
    )
```

**Actualización de Stock:**

```python
# Si cambia el stock, registrar movimiento
if stock_nuevo != stock_actual:
    diferencia = stock_nuevo - stock_actual
    tipo = 'ingreso' if diferencia > 0 else 'egreso'

    MovimientoStock.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=abs(diferencia),
        observacion=f'Ajuste manual por admin'
    )
```

---

### DELETE (Eliminar Producto)

**Verificaciones Pre-eliminación:**

```python
# Verificar si tiene pedidos asociados
if producto.pedidoitem_set.exists():
    raise ValidationError(
        "No se puede eliminar: producto tiene pedidos asociados"
    )

# Verificar si tiene movimientos
movimientos = producto.movimientostock_set.count()
if movimientos > 0:
    # Permitir pero advertir
    message = f"Producto tiene {movimientos} movimientos de stock"
```

**Proceso de Eliminación:**

1. Verificar dependencias
2. Solicitar confirmación al admin
3. Eliminar imagen de Spaces
4. Eliminar movimientos de stock (CASCADE)
5. Eliminar producto de BD
6. Mostrar confirmación

**Soft Delete (Alternativa):**

```python
# En lugar de DELETE, hacer UPDATE
producto.estado = 'descontinuado'
producto.save()
```

## Variantes del Escenario

### V1: Error al Subir Imagen

```
Paso 27: Spaces devuelve error (timeout, límite excedido)
    → Django captura excepción
    → No inserta producto en BD
    → Muestra error al admin
    → Admin puede reintentar
```

### V2: SKU Duplicado

```
Paso 24: Validación detecta SKU existente
    → Form devuelve error
    → Admin modifica SKU
    → Reenvía formulario
```

### V3: Producto con Pedidos Asociados

```
Paso 57: Al intentar eliminar producto con pedidos
    → Django detecta ForeignKey constraint
    → Rechaza eliminación
    → Sugiere desactivar en lugar de eliminar
```

## Métricas de Gestión

| Operación         | Tiempo Promedio | Frecuencia |
| ----------------- | --------------- | ---------- |
| Crear producto    | 2-3 minutos     | 5-10/día   |
| Editar producto   | 1-2 minutos     | 10-20/día  |
| Eliminar producto | 30 segundos     | 1-2/día    |
| Ver dashboard     | 5 segundos      | 20-30/día  |

## Mejoras Futuras

1. **Importación Masiva**: CSV para crear múltiples productos
2. **Historial de Cambios**: Auditoría de modificaciones
3. **Aprobación de Cambios**: Workflow de revisión
4. **Optimización de Imágenes**: Resize automático al subir
5. **Múltiples Imágenes**: Galería por producto
