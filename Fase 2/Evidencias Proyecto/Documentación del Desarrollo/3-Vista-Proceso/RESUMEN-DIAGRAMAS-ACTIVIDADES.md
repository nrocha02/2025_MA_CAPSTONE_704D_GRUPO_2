# 📋 Resumen: Diagramas de Actividades Creados

## Descripción General

Se han creado **5 diagramas de actividades** completos que documentan los procesos principales del sistema CordilleraPets eCommerce. Estos diagramas muestran el flujo de control de cada proceso, incluyendo todas las decisiones, validaciones, acciones y manejo de errores.

## Diagramas Creados

### 1. 🛒 Proceso de Compra Completa

**Archivo**: [`diagrama-actividad-compra-completa.md`](./diagrama-actividad-compra-completa.md)

**Descripción**: Flujo end-to-end desde la navegación del catálogo hasta la confirmación del pedido, incluyendo pago con Transbank.

**Fases del proceso**:

1. Navegación y Selección de Productos
2. Gestión del Carrito
3. Proceso de Checkout (datos de envío)
4. Transacción y Actualización de Stock (ACID)
5. Procesamiento de Pago con Transbank
6. Confirmación o Reversión

**Puntos de decisión críticos**:

- ¿Stock disponible? (3 niveles de validación)
- ¿Usuario registrado o invitado?
- ¿Stock final disponible con row locks?
- Resultado del pago: Aprobado / Rechazado / Timeout

**Características técnicas**:

- Transacciones ACID con `@transaction.atomic`
- Row-level locks con `SELECT FOR UPDATE`
- Integración con API Transbank
- Rollback automático en caso de error
- Generación de documentos tributarios

**Tiempo estimado**: 5-12 minutos (flujo completo sin problemas)

---

### 2. 🏪 Gestión de Productos (Dashboard Administrativo)

**Archivo**: [`diagrama-actividad-gestion-productos.md`](./diagrama-actividad-gestion-productos.md)

**Descripción**: Flujo completo de gestión administrativa de productos con operaciones CRUD completas e integración con DigitalOcean Spaces.

**Operaciones implementadas**:

- **Create**: Validación → Upload imagen → INSERT BD → Registro stock inicial
- **Read**: Listado con filtros (categoría, marca, estado) y búsqueda
- **Update**: Edición de datos, cambio de imagen, ajuste de stock
- **Delete**: Verificación de dependencias, eliminación física

**Validaciones clave**:

- SKU único en el sistema
- Slug único (generado automáticamente con sufijos)
- Imagen válida (formato JPG/PNG/WebP, tamaño < 5MB)
- No permitir eliminar productos con pedidos asociados

**Integración con Spaces**:

```python
# Upload mediante boto3 SDK
s3.upload_fileobj(imagen, bucket, f'productos/{slug}.jpg',
                  ExtraArgs={'ACL': 'public-read'})

# URL resultante
imagen_url = f"{CDN_URL}/productos/{slug}.jpg"
```

**Auditoría**:

- Todos los cambios de stock generan registros en `MovimientoStock`
- Logs detallados de todas las operaciones
- Usuario que realizó cada cambio

---

### 3. 🔐 Autenticación y Registro de Usuarios

**Archivo**: [`diagrama-actividad-autenticacion.md`](./diagrama-actividad-autenticacion.md)

**Descripción**: Flujos de seguridad para inicio de sesión, registro de usuarios, cierre de sesión y recuperación de contraseña.

**Flujos incluidos**:

1. **Inicio de Sesión**:

   - Validación de credenciales (email/RUT + contraseña)
   - Protección contra fuerza bruta (máximo 5 intentos)
   - Bloqueo temporal de 15 minutos
   - Verificación de cuenta activa
   - Creación de sesión Django
   - Restauración de carrito guardado

2. **Registro de Usuario**:

   - Validación de RUT chileno (formato y dígito verificador)
   - Validación de email único en el sistema
   - Validación de contraseña segura:
     - Mínimo 8 caracteres
     - Al menos 1 mayúscula
     - Al menos 1 minúscula
     - Al menos 1 número
     - Al menos 1 carácter especial
   - Hashing SHA-256 de contraseña
   - Creación de cuenta en BD

3. **Cerrar Sesión**:

   - Persistencia de carrito (si usuario registrado)
   - Destrucción de sesión
   - Limpieza de cookies
   - Registro en log de auditoría

4. **Recuperar Contraseña**:
   - Generación de token único (expira en 1 hora)
   - Envío de email con enlace
   - Protección contra enumeración de usuarios (mensaje genérico)

**Seguridad implementada**:

- Hashing de contraseñas (SHA-256)
- Límite de intentos fallidos
- Bloqueo temporal de cuenta
- Tokens de recuperación con expiración
- Auditoría completa de accesos

**Validación de RUT**:

```python
def validar_rut(rut):
    # Algoritmo de validación de RUT chileno
    # Calcula dígito verificador y compara
    return dv_calculado == dv_ingresado
```

---

### 4. 📦 Gestión de Inventario y Stock

**Archivo**: [`diagrama-actividad-gestion-inventario.md`](./diagrama-actividad-gestion-inventario.md)

**Descripción**: Gestión completa de inventario con movimientos de stock, sistema de alertas y auditoría exhaustiva.

**Operaciones de inventario**:

1. **Consultar Inventario**:

   - Listar productos con stock actual
   - Aplicar filtros (categoría, marca, estado)
   - Detectar productos con stock bajo
   - Resaltar alertas automáticamente

2. **Registrar Ingreso**:

   - Seleccionar producto
   - Ingresar cantidad y observaciones (proveedor, OC, etc.)
   - Transacción ACID: `stock = stock + cantidad`
   - INSERT movimiento tipo "ingreso"

3. **Registrar Egreso**:

   - Validar stock suficiente
   - Restar cantidad con row lock
   - Verificar si cae bajo stock mínimo
   - Generar alerta automática si es necesario
   - Notificar administrador

4. **Ajuste de Inventario**:

   - Ingresar stock real (conteo físico)
   - Calcular diferencia: `real - sistema`
   - Registrar ajuste positivo o negativo
   - Notificar sobre discrepancias significativas (> 10 unidades)

5. **Ver Historial de Movimientos**:

   - Listar movimientos por producto
   - Filtrar por rango de fechas
   - Calcular estadísticas (total ingresos, egresos, saldo)
   - Exportar a Excel (opcional)

6. **Configurar Stock Mínimo**:
   - Establecer umbral de alerta por producto
   - Sistema genera alerta automática cuando `stock <= stock_mínimo`

**Sistema de Alertas**:

| Tipo de Alerta    | Condición                | Acción                     |
| ----------------- | ------------------------ | -------------------------- | ----- | ----------------------- |
| Stock Bajo        | `stock <= stock_minimo`  | Notificación a admin       |
| Stock Crítico     | `stock <= stock_min / 2` | Email urgente              |
| Stock Agotado     | `stock == 0`             | Cambiar estado a "agotado" |
| Discrepancia Alta | `                        | ajuste                     | > 10` | Investigación requerida |

**Modelo de Auditoría**:

```python
class MovimientoStock:
    producto: FK
    tipo: ingreso | egreso | ajuste_positivo | ajuste_negativo | venta | devolucion
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    motivo: str
    observaciones: text
    usuario: FK  # Quien realizó el movimiento
    fecha: datetime
```

**Métricas KPI**:

- Rotación de Inventario: Ventas / Stock Promedio
- Días de Inventario: 365 / Rotación
- Tasa de Agotamiento: Productos Agotados / Total
- Exactitud de Inventario: 1 - (Ajustes / Stock Total)

---

### 5. 🔍 Navegación y Búsqueda en Catálogo

**Archivo**: [`diagrama-actividad-navegacion-catalogo.md`](./diagrama-actividad-navegacion-catalogo.md)

**Descripción**: Flujo detallado de navegación por el catálogo con búsqueda, filtrado, ordenamiento y visualización de productos.

**Flujos de navegación**:

1. **Ver Catálogo Completo**:

   - Query optimizado: `Producto.objects.select_related('categoria', 'marca')`
   - Carga de categorías y marcas para filtros
   - Renderizado de grid de productos
   - Lazy loading de imágenes desde CDN

2. **Buscar por Texto**:

   - Búsqueda en nombre y descripción (case-insensitive)
   - Query: `Q(nombre__icontains=termino) | Q(descripcion__icontains=termino)`
   - Validación de términos (no vacío)
   - Sugerencias cuando no hay resultados
   - Contador de resultados encontrados

3. **Filtrar por Categoría/Marca**:

   - Filtros individuales: `?categoria=slug` o `?marca=id`
   - Filtros combinados: `?categoria=slug&marca=id`
   - Resaltado de filtros activos en sidebar
   - Botón para limpiar todos los filtros

4. **Ordenar Resultados**:

   - Precio: Menor a Mayor (`ORDER BY precio ASC`)
   - Precio: Mayor a Menor (`ORDER BY precio DESC`)
   - Nombre: A-Z (`ORDER BY nombre ASC`)
   - Más Recientes (`ORDER BY fecha_creacion DESC`)

5. **Ver Detalle de Producto**:

   - Validación de existencia y estado activo
   - Carga de información completa del producto
   - Query de productos relacionados (misma categoría, límite 4)
   - Imágenes de alta resolución desde CDN

6. **Agregar al Carrito desde Detalle**:
   - Selección de cantidad con input numérico
   - Validación: `producto.stock >= cantidad`
   - Request AJAX asíncrono (sin recargar página)
   - Actualización de contador en badge
   - Toast de confirmación visual

**Optimizaciones de Performance**:

```python
# 1. Evitar N+1 Query Problem
productos = Producto.objects.select_related('categoria', 'marca')

# 2. Paginación
paginator = Paginator(productos, 24)  # 24 productos por página

# 3. Caché de listas estáticas
categorias = cache.get_or_set('categorias_activas',
                               lambda: list(Categoria.objects.filter(activa=True)),
                               3600)  # 1 hora

# 4. Lazy loading de imágenes (JavaScript)
<img data-src="{{ producto.imagen_url }}" class="lazy">
const observer = new IntersectionObserver(...);
```

**AJAX para Agregar al Carrito**:

```javascript
$.ajax({
  url: "/carrito/agregar/",
  type: "POST",
  data: {
    producto_id: productoId,
    cantidad: cantidad,
    csrfmiddlewaretoken: csrftoken,
  },
  success: function (response) {
    $("#carrito-count").text(response.total_productos);
    mostrarToast("Producto agregado", "success");
  },
});
```

**Métricas de UX**:

| Métrica                     | Objetivo     | Descripción                     |
| --------------------------- | ------------ | ------------------------------- |
| Tiempo Carga Catálogo       | < 1 segundo  | Request hasta render completo   |
| Tiempo Carga Imágenes       | < 2 segundos | Imágenes visibles cargadas      |
| Tasa Conversión Búsqueda    | > 60%        | Búsquedas que resultan en click |
| Productos Vistos por Sesión | > 5          | Promedio de productos vistos    |
| Tasa de Rebote Catálogo     | < 40%        | % usuarios que salen sin click  |

---

## Resumen Técnico

### Tecnologías Utilizadas

| Tecnología                | Uso                                        |
| ------------------------- | ------------------------------------------ |
| **Django ORM**            | Queries optimizadas con SELECT_RELATED     |
| **PostgreSQL**            | Base de datos con row-level locks          |
| **DigitalOcean Spaces**   | Almacenamiento S3-compatible para imágenes |
| **Transbank API**         | Procesamiento de pagos                     |
| **AJAX/jQuery**           | Interacciones asíncronas (carrito)         |
| **SHA-256**               | Hashing de contraseñas                     |
| **Django Cache**          | Caché de listas estáticas                  |
| **Intersection Observer** | Lazy loading de imágenes                   |

### Patrones de Diseño Implementados

1. **Transacciones ACID**: Integridad en operaciones críticas

   ```python
   @transaction.atomic
   def crear_pedido():
       # Todo o nada
   ```

2. **Row-Level Locks**: Control de concurrencia

   ```python
   producto = Producto.objects.select_for_update().get(id=producto_id)
   ```

3. **Query Optimization**: Evitar N+1 problem

   ```python
   productos = Producto.objects.select_related('categoria', 'marca')
   ```

4. **Repository Pattern**: Encapsulación de lógica de BD

   ```python
   class Carrito:
       def agregar(self, producto, cantidad):
           # Lógica de negocio
   ```

5. **State Machine**: Estados de pedido y producto
   ```python
   ESTADOS_PEDIDO = [
       ('pendiente_pago', 'Pendiente Pago'),
       ('pagado', 'Pagado'),
       # ...
   ]
   ```

### Validaciones Implementadas

| Validación        | Descripción                                   |
| ----------------- | --------------------------------------------- |
| Stock Disponible  | 3 niveles: UI, checkout, transacción          |
| SKU Único         | Verificación en BD antes de crear             |
| RUT Chileno       | Algoritmo de dígito verificador               |
| Email Válido      | Expresión regular + verificación única        |
| Contraseña Segura | 8+ chars, mayúsc, minúsc, números, especiales |
| Imagen Válida     | Formato (JPG/PNG/WebP) y tamaño (< 5MB)       |
| Cantidad Positiva | Cantidad > 0 en todas las operaciones         |

### Seguridad

| Mecanismo                  | Implementación                         |
| -------------------------- | -------------------------------------- |
| **Autenticación**          | Django Auth con sesiones               |
| **Autorización**           | `@login_required`, `@user_passes_test` |
| **Hashing de Contraseñas** | SHA-256                                |
| **Protección CSRF**        | Token CSRF en todos los formularios    |
| **SQL Injection**          | Django ORM escapa automáticamente      |
| **Fuerza Bruta**           | Límite de 5 intentos, bloqueo temporal |
| **Session Hijacking**      | HTTPS, cookies secure, httponly        |
| **File Upload Security**   | Validación de tipo MIME y extensión    |

### Auditoría y Logs

```python
# Logs implementados
logger.info(f"Pedido creado: {pedido_id}, Cliente: {cliente_id}")
logger.info(f"Producto creado: {producto.nombre}, Admin: {usuario}")
logger.warning(f"Stock bajo: Producto {producto_id}")
logger.warning(f"Login fallido: {username} desde {ip}")
logger.error(f"Error en transacción: {str(e)}")
logger.critical(f"Database connection lost")
```

### Métricas Agregadas

| Categoría              | Total |
| ---------------------- | ----- |
| Diagramas de Actividad | 5     |
| Flujos Principales     | 18+   |
| Puntos de Decisión     | 40+   |
| Validaciones           | 30+   |
| Transacciones ACID     | 8     |
| Integraciones Externas | 2     |

---

## Casos de Uso Validados

Estos 5 diagramas de actividad validan los siguientes casos de uso del sistema:

- ✅ UC-01: Navegar Catálogo
- ✅ UC-02: Buscar Productos
- ✅ UC-03: Ver Detalle Producto
- ✅ UC-04: Gestionar Carrito
- ✅ UC-05: Realizar Compra
- ✅ UC-06: Procesar Pago (Transbank)
- ✅ UC-07: Gestionar Productos (CRUD)
- ✅ UC-08: Gestionar Inventario
- ✅ UC-09: Subir Imágenes (DigitalOcean Spaces)
- ✅ UC-10: Autenticación y Autorización
- ✅ UC-11: Registro de Usuarios
- ✅ UC-12: Recuperación de Contraseña

---

## Conclusión

Los 5 diagramas de actividades creados proporcionan una documentación completa y detallada de los procesos principales del sistema CordilleraPets eCommerce. Cada diagrama incluye:

✅ **Flujos completos** desde inicio hasta fin  
✅ **Todos los puntos de decisión** con criterios claros  
✅ **Validaciones en múltiples niveles** (UI, lógica, BD)  
✅ **Manejo robusto de errores** con rollbacks  
✅ **Integraciones con servicios externos** (Transbank, Spaces)  
✅ **Optimizaciones de performance** (queries, caché, lazy loading)  
✅ **Seguridad en cada paso** (autenticación, validación, auditoría)  
✅ **Código de ejemplo** para implementación  
✅ **Métricas y KPIs** para monitoreo

**Aspectos destacados del diseño arquitectónico:**

- Transacciones ACID para integridad de datos
- Control de concurrencia con row-level locks
- Arquitectura escalable con múltiples workers
- Separación de responsabilidades (MVC)
- Auditoría completa de operaciones críticas
- Experiencia de usuario optimizada

---

**Documentación Completa**: Octubre 2025  
**Sistema**: CordilleraPets eCommerce  
**Versión**: 1.0  
**Total de Diagramas de Actividades**: 5

---

**Archivos de Diagramas**:

1. [`diagrama-actividad-compra-completa.md`](./diagrama-actividad-compra-completa.md)
2. [`diagrama-actividad-gestion-productos.md`](./diagrama-actividad-gestion-productos.md)
3. [`diagrama-actividad-autenticacion.md`](./diagrama-actividad-autenticacion.md)
4. [`diagrama-actividad-gestion-inventario.md`](./diagrama-actividad-gestion-inventario.md)
5. [`diagrama-actividad-navegacion-catalogo.md`](./diagrama-actividad-navegacion-catalogo.md)
