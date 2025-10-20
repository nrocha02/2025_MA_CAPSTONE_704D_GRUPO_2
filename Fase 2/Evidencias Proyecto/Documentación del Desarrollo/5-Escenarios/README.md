# Escenarios (Casos de Uso)

## Descripción General

Los Escenarios representan la vista "+1" del modelo arquitectónico 4+1. Esta vista ilustra cómo las otras cuatro vistas trabajan juntas a través de casos de uso concretos que validan y demuestran la arquitectura del sistema.

## Propósito

Esta vista permite:

- Validar las decisiones arquitectónicas
- Demostrar el funcionamiento del sistema
- Identificar casos de uso críticos
- Verificar que todas las vistas trabajan coherentemente
- Documentar flujos de usuario principales

## Contenido

1. [Actores del Sistema](#actores-del-sistema)
2. [Casos de Uso Principales](#casos-de-uso-principales)
3. [Escenarios Detallados](#escenarios-detallados)
4. [Casos de Uso del Sistema](#casos-de-uso-del-sistema)

---

## Actores del Sistema

📄 **[Ver diagrama de actores del sistema](./diagrama-actores.md)**

Actores principales y secundarios que interactúan con el sistema.

### Descripción de Actores

| Actor                   | Descripción                        | Privilegios                                                    |
| ----------------------- | ---------------------------------- | -------------------------------------------------------------- |
| **Cliente Anónimo**     | Usuario que navega sin registrarse | Ver catálogo, agregar al carrito, comprar como invitado        |
| **Cliente Registrado**  | Usuario con cuenta personal        | Todo lo anterior + historial de compras, direcciones guardadas |
| **Cliente Empresa**     | Cliente corporativo registrado     | Todo lo anterior + facturación empresarial                     |
| **Administrador**       | Gestor del sistema                 | CRUD productos, categorías, marcas, ver pedidos                |
| **Vendedor**            | Personal de sucursal               | Consultar inventario, crear pedidos presenciales               |
| **Sistema Transbank**   | Plataforma de pagos                | Procesar pagos, notificar resultados                           |
| **DigitalOcean Spaces** | Servicio de almacenamiento         | Almacenar y servir imágenes                                    |

---

## Casos de Uso Principales

📄 **[Ver diagrama de casos de uso completo](./diagrama-casos-uso.md)**

Casos de uso principales organizados por actor.

### Resumen de Casos de Uso

**Cliente Anónimo:**

- UC-01: Navegar Catálogo
- UC-02: Buscar Productos
- UC-03: Ver Detalle Producto
- UC-04: Gestionar Carrito
- UC-05: Realizar Compra

**Cliente Registrado:**

- Todo lo anterior
- UC-11: Ver Historial de Compras
- UC-12: Gestionar Direcciones

**Administrador:**

- UC-07: Gestionar Productos (incluye UC-09: Subir Imágenes)
- UC-08: Gestionar Categorías
- UC-10: Ver Dashboard

**Sistemas Externos:**

- UC-06: Procesar Pago (Transbank)
- UC-09: Subir Imágenes (DigitalOcean Spaces)

---

## Escenarios Detallados

### Escenario 1: Compra de Producto por Cliente Anónimo

📄 **[Ver diagrama completo del escenario de compra](./escenario-compra-completa.md)**

**Objetivo**: Validar el flujo completo desde la navegación hasta la compra como invitado.

**Actores**: Cliente Anónimo, Sistema Transbank, DigitalOcean Spaces

**Precondiciones**:

- El catálogo tiene productos activos con stock
- Las imágenes están disponibles en DO Spaces
- Transbank está operativo

**Fases del Proceso**:

1. **Navegación**: Cliente accede al sitio y visualiza productos
2. **Búsqueda y Filtrado**: Filtra productos por categoría
3. **Detalle de Producto**: Visualiza información completa del producto
4. **Agregar al Carrito**: Selecciona cantidad y agrega
5. **Ver Carrito**: Revisa resumen de compra
6. **Checkout**: Completa formulario como invitado
7. **Pago**: Procesa pago con Transbank
8. **Confirmación**: Recibe confirmación y número de pedido

**Postcondiciones**:

- Pedido creado en estado "Pagado"
- Stock actualizado
- Documento tributario generado
- Carrito vaciado
- Sesión de invitado registrada

**Variantes**:

- V1: Cliente se registra durante el checkout
- V2: Pago rechazado por Transbank
- V3: Stock insuficiente al momento de confirmar

---

### Escenario 2: Gestión de Productos por Administrador

📄 **[Ver diagrama completo del escenario de gestión de productos](./escenario-gestion-productos.md)**

**Objetivo**: Validar el flujo completo de administración de productos.

**Actores**: Administrador, DigitalOcean Spaces

**Precondiciones**:

- Administrador autenticado en dashboard
- Categorías y marcas ya existen

**Fases del Proceso**:

1. **Acceso al Dashboard**: Administrador ingresa al panel
2. **Crear Nuevo Producto**: Accede al formulario de creación
3. **Subir Imagen**: Carga imagen a DigitalOcean Spaces
4. **Guardar Producto**: Registra producto en base de datos
5. **Actualizar Stock**: Registra movimiento de stock inicial
6. **Confirmar**: Visualiza producto creado

**Datos de Ejemplo**:

- Nombre: Alimento Royal Canin Adulto
- SKU: RC-ADULTO-15KG
- Precio: 45,990
- Stock: 50
- Categoría: Alimento Perro
- Marca: Royal Canin

**Postcondiciones**:

- Producto creado y activo
- Imagen almacenada en Spaces con URL CDN
- Movimiento de stock inicial registrado
- Slug generado automáticamente

**Variantes**:

- V1: Editar producto existente
- V2: Eliminar producto (soft delete)
- V3: Error al subir imagen (timeout, límite tamaño)
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

**Postcondiciones**:
- Producto creado/actualizado/eliminado en BD
- Imagen subida/actualizada/eliminada en Spaces
- Movimientos de stock registrados
- Dashboard actualizado con nuevas métricas

**Variantes**:
- **V1**: Error al subir imagen (timeout, tamaño excedido)
- **V2**: Producto con pedidos asociados (no se puede eliminar)
- **V3**: SKU duplicado (validación falla)

---

### Escenario 3: Actualización de Stock en Tiempo Real

📄 **[Ver diagrama completo del escenario de concurrencia de stock](./escenario-concurrencia-stock.md)**

**Objetivo**: Validar la concurrencia en actualización de stock.

**Actores**: 2 Clientes simultáneos

**Precondiciones**:
- Producto con stock limitado (ej: 3 unidades)

**Situación de Concurrencia**:

**Estado Inicial**: Producto X tiene stock = 3 unidades

**Eventos Simultáneos**:
1. Cliente 1 intenta comprar 2 unidades
2. Cliente 2 intenta comprar 2 unidades (al mismo tiempo)

**Mecanismo de Control**:
- `SELECT ... FOR UPDATE` adquiere row lock
- Transacciones garantizan aislamiento
- El segundo cliente espera por el lock
- Verificación de stock dentro de transacción

**Resultado**:
1. Cliente 1: Compra exitosa (stock: 3 → 1)
2. Cliente 2: Error "Stock insuficiente" (1 < 2)

**Postcondiciones**:
- Integridad de stock mantenida
- No se vende más unidades que las disponibles
- Transacciones ACID garantizadas

---

## Casos de Uso del Sistema

📄 **[Ver diagramas de flujos completos](./diagramas-flujos.md)**

Flujos detallados de los casos de uso principales del sistema.

### UC-01: Navegar Catálogo

**Descripción**: El usuario navega por el catálogo de productos, aplicando filtros opcionales.

**Actores**: Cliente Anónimo / Cliente Registrado

**Entrada**: Ninguna o parámetros de filtro (categoría, marca, búsqueda)

**Salida**: Lista de productos que coinciden con los criterios

**Validaciones**:
- Solo productos con estado 'activo' son visibles
- Categorías y marcas deben estar activas

**Flujo Principal**:
1. Usuario accede al sitio
2. Sistema muestra productos activos
3. Usuario puede filtrar por categoría/marca
4. Sistema carga productos filtrados
5. Usuario puede buscar por texto
6. Sistema muestra resultados
7. Imágenes se cargan desde Spaces

---

### UC-02: Gestionar Carrito de Compras

**Descripción**: El usuario gestiona los productos en su carrito de compras.

**Actores**: Cliente Anónimo / Cliente Registrado

**Estados del Carrito**:
- Vacío: No hay productos
- Con Items: Tiene 1+ productos
- Actualizando: Modificando cantidad
- Error: Stock insuficiente

**Operaciones**:
- Agregar producto al carrito
- Actualizar cantidad
- Eliminar producto
- Limpiar carrito
- Ver resumen

**Validaciones**:
- Stock disponible >= cantidad solicitada
- Cantidad > 0
- Producto activo
    [*] --> CarritoVacio

    CarritoVacio --> CarritoConItems: Agregar primer producto

    CarritoConItems --> CarritoConItems: Agregar producto
    CarritoConItems --> CarritoConItems: Actualizar cantidad
    CarritoConItems --> CarritoConItems: Eliminar un producto
    CarritoConItems --> CarritoVacio: Eliminar todos los productos

    CarritoConItems --> VerificandoStock: Proceder al checkout

    VerificandoStock --> CarritoConItems: Stock insuficiente
    VerificandoStock --> Checkout: Stock disponible

    Checkout --> [*]: Compra exitosa
    Checkout --> CarritoConItems: Cancelar compra

    CarritoVacio --> [*]: Cerrar sesión
    CarritoConItems --> [*]: Expirar sesión (24h)
```

**Descripción**: El usuario gestiona los productos en su carrito de compras.

**Operaciones**:

1. **Agregar**: Añade producto con cantidad especificada
2. **Actualizar**: Modifica cantidad de un producto existente
3. **Eliminar**: Quita un producto del carrito
4. **Ver**: Muestra resumen con totales

**Reglas de Negocio**:

- Cantidad mínima: 1
- Cantidad máxima: Stock disponible
- Costo de envío fijo: $2,990
- Almacenamiento: Sesión Django (24h)

---

### UC-03: Realizar Compra

**Descripción**: Proceso completo de checkout y pago.

**Actores**: Cliente Anónimo / Cliente Registrado / Cliente Empresa, Transbank

**Precondiciones**:

- Carrito con al menos un producto
- Stock disponible para todos los items

**Flujo Principal**:

1. Usuario inicia checkout desde carrito
2. Sistema verifica si usuario está registrado
3. Si registrado: carga datos guardados
4. Si invitado: solicita datos de envío
5. Usuario completa/valida datos
6. Sistema inicia transacción
7. Sistema verifica stock con locks
8. Sistema crea pedido e items
9. Sistema actualiza stock
10. Sistema inicia pago con Transbank
11. Usuario completa pago
12. Sistema procesa resultado
13. Si aprobado: genera documento tributario
14. Si rechazado: revierte stock
15. Sistema limpia carrito
16. Sistema muestra confirmación

**Postcondiciones Éxito**:

- Pedido creado en estado "Pagado"
- Stock actualizado
- Documento tributario generado (boleta o factura)
- Carrito limpiado
- Movimientos de stock registrados

**Casos de Error**:

- Stock insuficiente → Rollback, mensaje de error
- Pago rechazado → Pedido cancelado, stock revertido
- Timeout Transbank → Verificación manual pendiente

**Postcondiciones Fallo**:

- Stock no modificado
- Pedido cancelado o no creado
- Carrito preservado

---

### UC-04: Administrar Productos (Dashboard)

**Diagrama de Casos de Uso del Dashboard**:

```mermaid
graph TB
    subgraph "Dashboard Admin"
        UC7[UC-07: Crear Producto]
        UC7A[UC-07a: Editar Producto]
        UC7B[UC-07b: Eliminar Producto]
        UC7C[UC-07c: Ver Listado]

        UC8[UC-08: Crear Categoría]
        UC8A[UC-08a: Editar Categoría]
        UC8B[UC-08b: Eliminar Categoría]

        UC9[UC-09: Subir Imagen]
        UC9A[UC-09a: Eliminar Imagen]

        UC10[UC-10: Ver Dashboard]
    end

    Admin[Administrador] --> UC7
    Admin --> UC7A
    Admin --> UC7B
    Admin --> UC7C
    Admin --> UC8
    Admin --> UC8A
    Admin --> UC8B
    Admin --> UC10

    UC7 ..> UC9: include
    UC7A ..> UC9: include
    UC7A ..> UC9A: include
    UC7B ..> UC9A: include

    Spaces[DO Spaces] --> UC9
    Spaces --> UC9A
```

---

### UC-04: Administrar Productos

**Descripción**: El administrador gestiona el catálogo de productos.

**Actores**: Administrador, DigitalOcean Spaces

**Operaciones CRUD**:

**1. Create (Crear)**:

- Validar datos del formulario
- Generar slug único a partir del nombre
- Subir imagen a DigitalOcean Spaces
- Insertar producto en base de datos
- Registrar movimiento de stock inicial

**2. Read (Leer)**:

- Listar productos con paginación
- Filtrar por categoría, marca, estado
- Buscar por nombre o SKU
- Ver detalles completos de producto

**3. Update (Actualizar)**:

- Validar cambios en datos
- Actualizar imagen (eliminar anterior si cambia)
- Actualizar registro en base de datos
- Registrar movimientos de stock si cantidad cambia

**4. Delete (Eliminar)**:

- Verificar dependencias (productos con pedidos no se eliminan)
- Eliminar imagen de DigitalOcean Spaces
- Eliminar registro de BD (CASCADE elimina movimientos asociados)

**Validaciones**:

- SKU único
- Precio > 0
- Stock >= 0
- Categoría y marca deben existir
- Imagen: formatos permitidos (JPG, PNG, WebP), tamaño < 5MB

---

## Matriz de Trazabilidad

### Relación entre Casos de Uso y Vistas Arquitectónicas

| Caso de Uso                  | Vista Lógica         | Vista Desarrollo     | Vista Proceso    | Vista Física            |
| ---------------------------- | -------------------- | -------------------- | ---------------- | ----------------------- |
| UC-01: Navegar Catálogo      | Subsistema Ventas    | `ventas/views.py`    | Request-response | App Server → DB, Spaces |
| UC-02: Gestionar Carrito     | Subsistema Carrito   | `carrito/carrito.py` | Session storage  | App Server → Session    |
| UC-03: Realizar Compra       | Pedidos + Clientes   | `checkout/views.py`  | Transacción ACID | App → DB → Transbank    |
| UC-04: Administrar Productos | Subsistema Productos | `dashboard/views.py` | CRUD + upload    | App → DB, Spaces        |

---

## Escenarios de Rendimiento

### Escenario P-01: Carga Concurrente

**Objetivo**: Sistema debe soportar 100 usuarios concurrentes navegando el catálogo.

**Métricas Esperadas**:

- Response time < 500ms (p95)
- Error rate < 1%
- Throughput: 200 requests/segundo

**Arquitectura de Validación**:

- 100 usuarios → Load Balancer
- Load Balancer → 2 App Servers (4 workers cada uno)
- App Servers → PostgreSQL + Redis Cache

---

### Escenario P-02: Checkout Simultáneo

**Objetivo**: Procesar 10 checkouts simultáneos sin race conditions.

**Mecanismo**: Row-level locks (`SELECT ... FOR UPDATE`) en PostgreSQL garantizan integridad de stock.

---

## Escenarios de Seguridad

### Escenario S-01: Protección de Dashboard

**Prueba**: Atacante intenta acceder a `/dashboard/` sin autenticación.

**Resultado Esperado**:

- Sistema verifica autenticación
- Redirecciona a `/login/`
- Acceso denegado

**Validación**: Todas las vistas de dashboard utilizan `@login_required` decorator.

---

### Escenario S-02: Protección contra Inyección SQL

**Prueba**: Intento de inyección mediante parámetro malicioso.

```python
# Intento de inyección
categoria = "perro' OR '1'='1"
```

**Protección**: Django ORM escapa automáticamente todos los parámetros.

```python
# Query segura generada por ORM
Producto.objects.filter(categoria__slug=categoria)
# SQL resultante: WHERE categoria.slug = 'perro'' OR ''1''=''1'
# (comillas escapadas, no ejecuta lógica maliciosa)
```

---

## 📊 Índice de Diagramas

📄 **[Ver índice completo de diagramas de esta vista](./DIAGRAMAS.md)**

El índice contiene enlaces directos a todos los diagramas de escenarios y casos de uso con descripciones detalladas.

---

## Conclusión

Los Escenarios validan que las cuatro vistas arquitectónicas trabajan coherentemente para proporcionar la funcionalidad completa del sistema Cordillera Pets eCommerce.

**Casos de Uso Validados**:

- ✅ Navegación y búsqueda de productos
- ✅ Gestión de carrito de compras
- ✅ Proceso de checkout y pago
- ✅ Administración de productos
- ✅ Upload de imágenes a cloud storage
- ✅ Control de concurrencia en stock

**Atributos de Calidad Verificados**:

- **Funcionalidad**: Todos los casos de uso implementados
- **Rendimiento**: Arquitectura escalable (100+ usuarios concurrentes)
- **Seguridad**: Autenticación, validación, protección SQL injection
- **Confiabilidad**: Transacciones ACID, control de concurrencia
- **Usabilidad**: Flujos claros e intuitivos
- **Mantenibilidad**: Código organizado y documentado
