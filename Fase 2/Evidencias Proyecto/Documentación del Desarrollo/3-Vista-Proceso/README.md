# Vista de Proceso

## Descripción General

La Vista de Proceso describe los aspectos dinámicos del sistema, incluyendo procesos, threads, comunicación entre procesos, sincronización y el comportamiento en tiempo de ejecución.

## Propósito

Esta vista permite entender:

- Los procesos principales del sistema
- Los flujos de trabajo (workflows)
- La concurrencia y paralelismo
- Los estados y transiciones
- El comportamiento en tiempo de ejecución

## Contenido

1. [Procesos Principales](#procesos-principales)
2. [Flujos de Trabajo](#flujos-de-trabajo)
3. [Diagramas de Secuencia](#diagramas-de-secuencia)
4. [Diagramas de Actividades](#diagramas-de-actividades)
5. [Diagrama de Estados](#diagrama-de-estados)
6. [Concurrencia y Performance](#concurrencia-y-performance)

---

## Procesos Principales

### Arquitectura de Procesos del Sistema

📄 **[Ver diagrama completo: Arquitectura de Procesos](./diagrama-arquitectura-procesos.md)**

El sistema sigue una arquitectura de múltiples workers con servicios externos.

**Componentes principales:**

- **Cliente Web**: Navegador del usuario con JavaScript
- **WSGI Server**: Gunicorn/uWSGI con múltiples workers
- **Django Application**: Lógica de negocio en cada worker
- **PostgreSQL**: Base de datos con connection pool
- **DigitalOcean Spaces**: Almacenamiento S3-compatible
- **Transbank API**: Pasarela de pagos

---

## Flujos de Trabajo

### 1. Flujo de Navegación del Catálogo

📄 **[Ver diagrama de secuencia completo](./diagrama-flujo-catalogo.md)**

Proceso de navegación por el catálogo con carga de imágenes desde Spaces.

**Pasos principales:**

1. Request HTTP GET a /catalogo/
2. Query a base de datos (productos activos)
3. Aplicación de filtros (categoría, marca)
4. Renderizado de template en servidor
5. Carga paralela de imágenes desde CDN

### 2. Flujo de Gestión del Carrito

📄 **[Ver diagrama de secuencia completo](./diagrama-flujo-carrito.md)**

Proceso de agregar productos al carrito con verificación de stock en tiempo real.

**Características:**

- Request AJAX asíncrono
- Verificación de stock disponible
- Almacenamiento en sesión Django
- Respuesta JSON ligera
- Actualización inmediata del contador en UI

### 3. Flujo de Creación de Producto (Dashboard)

📄 **[Ver diagrama de secuencia completo](./diagrama-flujo-crear-producto.md)**

Proceso completo de creación de productos desde el dashboard administrativo.

**Fases del proceso:**

1. Validación de datos del formulario
2. Generación de slug único
3. Upload de imagen a DigitalOcean Spaces (boto3 SDK)
4. Inserción en base de datos
5. Registro de movimiento de stock inicial
6. Redirect con confirmación

### 4. Flujo de Checkout y Pago

📄 **[Ver diagrama de secuencia completo](./diagrama-flujo-checkout.md)**

Proceso completo de checkout con transacciones ACID e integración con Transbank.

**Fases principales:**

1. **Preparación**: Validación de carrito y formulario de datos
2. **Creación de Pedido**: Transacción ACID con actualización de stock
3. **Procesamiento de Pago**: Integración con API Transbank
4. **Confirmación**: Generación de documento tributario o reversión

**Componentes críticos:**

- Transacciones ACID (todo o nada)
- SELECT FOR UPDATE (row locks para stock)
- Manejo de callbacks de Transbank
- Reversión automática en caso de error

---

## Diagramas de Secuencia

### Secuencia: Búsqueda y Filtrado de Productos

📄 **[Ver diagrama de secuencia completo](./diagrama-secuencia-busqueda.md)**

Interacción entre las capas del sistema (patrón MVC de Django) durante búsqueda.

**Patrón MVC:**

- **Vista (Browser)**: Interfaz de usuario
- **Controlador (Django View)**: Lógica de negocio
- **Modelo (ORM)**: Abstracción de base de datos
- **Base de Datos**: PostgreSQL

**Queries ejecutados:**

1. Productos filtrados (con JOIN a categoría y marca)
2. Categorías activas (para sidebar)
3. Marcas activas (para filtros adicionales)

### Secuencia: Actualización de Cantidad en Carrito

📄 **[Ver diagrama de secuencia completo](./diagrama-secuencia-actualizar-carrito.md)**

Flujo detallado de actualización de cantidad con la clase Carrito.

**Clase Carrito:**

- Inicialización desde sesión Django
- Operaciones: agregar, actualizar, eliminar
- Cálculos: subtotales, total, envío
- Persistencia en sesión

**Almacenamiento:**

```python
carrito = {
    "5": {
        "producto_id": 5,
        "cantidad": 3,
        "precio": 45990,
        # ...
    }
}
```

---

## Diagramas de Actividades

📁 **[Ver carpeta completa: Diagramas de Actividades](./diagramas-actividades/)**

Los diagramas de actividades muestran el flujo de control completo de los procesos principales del sistema, incluyendo todas las decisiones, validaciones y acciones en cada fase.

### Actividad: Proceso de Compra Completa

📄 **[Ver diagrama completo: Proceso de Compra](./diagramas-actividades/diagrama-actividad-compra-completa.md)**

Flujo end-to-end desde que el cliente navega el catálogo hasta que recibe la confirmación del pedido.

**Fases del proceso:**

1. **Navegación y Selección**: Explorar catálogo, buscar, filtrar productos
2. **Gestión del Carrito**: Agregar, modificar cantidades, eliminar items
3. **Checkout**: Datos de envío (registrado o invitado)
4. **Transacción de Stock**: Verificación y bloqueo con SELECT FOR UPDATE
5. **Procesamiento de Pago**: Integración con Transbank
6. **Confirmación**: Generación de documento o reversión de stock

**Puntos de decisión críticos:**

- ¿Stock disponible? (3 niveles de validación)
- ¿Usuario registrado o invitado?
- ¿Stock final disponible? (con row locks)
- Resultado del pago: Aprobado / Rechazado / Timeout

### Actividad: Gestión de Productos (Dashboard)

📄 **[Ver diagrama completo: Gestión de Productos](./diagramas-actividades/diagrama-actividad-gestion-productos.md)**

Flujo completo de administración de productos desde el dashboard con operaciones CRUD.

**Operaciones implementadas:**

- **Create**: Formulario → Validación → Upload imagen (Spaces) → INSERT BD → Movimiento stock inicial
- **Read**: Listar con filtros (categoría, marca, estado) y búsqueda (SKU, nombre)
- **Update**: Editar datos → Cambiar imagen (opcional) → Registrar cambio de stock
- **Delete**: Verificar dependencias → Eliminar de BD → Eliminar imagen de Spaces

**Validaciones clave:**

- SKU único
- Slug único (generado automáticamente)
- Imagen válida (formato, tamaño)
- No eliminar productos con pedidos asociados

### Actividad: Autenticación y Registro

📄 **[Ver diagrama completo: Autenticación](./diagramas-actividades/diagrama-actividad-autenticacion.md)**

Flujos de seguridad para gestión de usuarios y accesos.

**Flujos incluidos:**

1. **Inicio de Sesión**:

   - Validación de credenciales (email/RUT + contraseña)
   - Protección contra fuerza bruta (máx. 5 intentos)
   - Bloqueo temporal (15 minutos)
   - Creación de sesión Django

2. **Registro de Usuario**:

   - Validación de RUT chileno (formato y dígito verificador)
   - Validación de email único
   - Validación de contraseña segura (8+ chars, mayúsc, minúsc, números, especiales)
   - Hashing SHA-256
   - Creación de cuenta

3. **Recuperación de Contraseña**:
   - Generación de token único (expira en 1 hora)
   - Envío de email con enlace
   - Protección contra enumeración de usuarios

**Seguridad implementada:**

- Hashing de contraseñas (SHA-256)
- Límite de intentos fallidos
- Bloqueo temporal de cuenta
- Tokens de recuperación con expiración
- Auditoría de accesos

### Actividad: Gestión de Inventario y Stock

📄 **[Ver diagrama completo: Gestión de Inventario](./diagramas-actividades/diagrama-actividad-gestion-inventario.md)**

Gestión completa de inventario con movimientos de stock, alertas y auditoría.

**Operaciones de inventario:**

1. **Consultar Inventario**:

   - Listar productos con stock actual
   - Aplicar filtros (categoría, marca, estado)
   - Detectar productos con stock bajo
   - Resaltar alertas

2. **Registrar Ingreso**:

   - Seleccionar producto
   - Ingresar cantidad y observaciones
   - Transacción ACID: UPDATE stock + INSERT movimiento

3. **Registrar Egreso**:

   - Validar stock suficiente
   - Restar cantidad con row lock
   - Generar alerta si stock bajo
   - Notificar administrador

4. **Ajuste de Inventario**:

   - Ingresar stock real (conteo físico)
   - Calcular diferencia (real - sistema)
   - Registrar ajuste positivo o negativo
   - Notificar sobre discrepancias significativas

5. **Ver Historial**:

   - Listar movimientos por producto
   - Filtrar por rango de fechas
   - Calcular estadísticas (ingresos, egresos, saldo)
   - Exportar a Excel (opcional)

6. **Configurar Stock Mínimo**:
   - Establecer umbral de alerta por producto
   - Sistema genera alerta automática cuando stock <= mínimo

**Sistema de Alertas:**

| Tipo          | Condición                   | Acción                     |
| ------------- | --------------------------- | -------------------------- | -------------- | ----------------------- |
| Stock Bajo    | `stock <= stock_minimo`     | Notificación a admin       |
| Stock Crítico | `stock <= stock_minimo / 2` | Email urgente              |
| Stock Agotado | `stock == 0`                | Cambiar estado a "agotado" |
| Discrepancia  | `                           | ajuste                     | > 10 unidades` | Investigación requerida |

**Tabla de Auditoría: MovimientoStock**

```python
class MovimientoStock:
    - producto: FK
    - tipo: ingreso | egreso | ajuste_positivo | ajuste_negativo | venta | devolucion
    - cantidad: int
    - stock_anterior: int
    - stock_nuevo: int
    - motivo: str
    - observaciones: text
    - usuario: FK (quien realizó el movimiento)
    - fecha: datetime
```

### Actividad: Navegación y Búsqueda en Catálogo

📄 **[Ver diagrama completo: Navegación en Catálogo](./diagramas-actividades/diagrama-actividad-navegacion-catalogo.md)**

Flujo detallado de navegación por el catálogo con búsqueda, filtrado y visualización de productos.

**Flujos de navegación:**

1. **Ver Catálogo Completo**:

   - Query optimizado con SELECT_RELATED
   - Carga de categorías y marcas para filtros
   - Renderizado de grid de productos
   - Lazy loading de imágenes desde CDN

2. **Buscar por Texto**:

   - Búsqueda en nombre y descripción (case-insensitive)
   - Validación de términos
   - Sugerencias cuando no hay resultados
   - Contador de resultados encontrados

3. **Filtrar por Categoría/Marca**:

   - Filtros individuales o combinados
   - Parámetros en URL (?categoria=slug&marca=id)
   - Resaltado de filtros activos en sidebar
   - Botón para limpiar filtros

4. **Ordenar Resultados**:

   - Precio: Menor a Mayor / Mayor a Menor
   - Nombre: A-Z
   - Más Recientes (por fecha de creación)
   - Más Vendidos (opcional)

5. **Ver Detalle de Producto**:

   - Validación de existencia y estado activo
   - Carga de información completa
   - Productos relacionados (misma categoría)
   - Validación de stock antes de agregar al carrito

6. **Agregar al Carrito**:
   - Selección de cantidad
   - Validación de stock disponible
   - Request AJAX asíncrono
   - Actualización de contador sin recargar página
   - Toast de confirmación

**Optimizaciones implementadas:**

```python
# 1. SELECT_RELATED para evitar N+1 queries
productos = Producto.objects.select_related('categoria', 'marca')

# 2. Paginación
from django.core.paginator import Paginator
paginator = Paginator(productos, 24)  # 24 por página

# 3. Caché de listas estáticas
from django.core.cache import cache
categorias = cache.get_or_set('categorias_activas',
                               lambda: list(Categoria.objects.filter(activa=True)),
                               3600)

# 4. Lazy loading de imágenes (JavaScript)
<img data-src="{{ producto.imagen_url }}" class="lazy">
```

**Métricas de UX:**

| Métrica                  | Objetivo     | Descripción                     |
| ------------------------ | ------------ | ------------------------------- |
| Tiempo Carga Catálogo    | < 1 segundo  | Request hasta render completo   |
| Tiempo Carga Imágenes    | < 2 segundos | Imágenes visibles cargadas      |
| Tasa Conversión Búsqueda | > 60%        | Búsquedas que resultan en click |
| Productos por Sesión     | > 5          | Promedio de productos vistos    |

---

## Diagrama de Estados

📄 **[Ver diagramas de estados completos](./diagramas-estados.md)**

El sistema implementa máquinas de estados para las entidades principales.

### Estados del Pedido

- **Flujo normal**: Pendiente_Pago → Pagado → En_Preparacion → Enviado → En_Transito → Entregado
- **Cancelación**: Desde cualquier estado (excepto Entregado)
- **Devolución**: Desde En_Transito
- **Timeout**: 15 minutos en Pendiente_Pago

### Estados del Producto

- **Activo**: Visible y disponible para venta
- **Inactivo**: No visible temporalmente
- **Agotado**: Visible pero sin stock
- **Descontinuado**: Estado final (no visible)

### Estados de la Sesión del Carrito

- **Vacio**: Carrito recién creado
- **Con_Items**: Uno o más productos
- **Checkout**: En proceso de pago
- **Timeout**: 24 horas

---

## Concurrencia y Performance

### Modelo de Concurrencia

📄 **[Ver diagrama de concurrencia completo](./diagrama-concurrencia.md)**

Arquitectura de múltiples workers con connection pooling a base de datos.

**Configuración:**

- **Gunicorn Workers**: (2 x CPU cores) + 1 = 4 workers
- **Connection Pool**: Máximo 20 conexiones a PostgreSQL
- **Worker Class**: Sync (un thread por request)

### Estrategias de Performance

#### 1. Query Optimization

```python
# ❌ N+1 Query Problem
productos = Producto.objects.all()
for producto in productos:
    print(producto.categoria.nombre)  # Query por cada producto

# ✅ Select Related (1 Query con JOIN)
productos = Producto.objects.select_related('categoria', 'marca').all()
for producto in productos:
    print(producto.categoria.nombre)  # No queries adicionales
```

#### 2. Caching Strategy (Futuro)

- L1 Cache: Memoria local por proceso
- L2 Cache: Redis compartido
- L3 Cache: Base de datos

#### 3. Session Storage

- **Backend**: Database-backed sessions (PostgreSQL)
- **Alternativa futura**: Redis para mejor performance
- **Timeout**: 24 horas para carritos

#### 4. Static Files Serving

- **CSS/JS**: Servidos directamente por Nginx
- **Imágenes**: CDN de DigitalOcean Spaces
- **Contenido dinámico**: Django Application

---

## Procesos de Sincronización

### Control de Concurrencia en Pedidos

📄 **[Ver diagrama de sincronización completo](./diagrama-sincronizacion.md)**

El sistema implementa row-level locks para prevenir race conditions en actualización de stock.

**Mecanismos de sincronización:**

- **SELECT FOR UPDATE**: Row-level locks en PostgreSQL
- **Transacciones ACID**: @transaction.atomic en Django
- **Isolation Level**: READ COMMITTED (default)
- **Deadlock Detection**: Automático en PostgreSQL

### Manejo de Transacciones

```python
from django.db import transaction

@transaction.atomic
def crear_pedido(carrito, cliente):
    # Todo dentro de una transacción
    pedido = Pedido.objects.create(...)

    for item in carrito.items():
        # Verificar y actualizar stock
        producto = Producto.objects.select_for_update().get(id=item.id)
        if producto.stock >= item.cantidad:
            producto.stock -= item.cantidad
            producto.save()
            PedidoItem.objects.create(...)
        else:
            raise ValueError("Stock insuficiente")

    # Si algo falla, todo se revierte automáticamente
    return pedido
```

---

## Procesos de Background (Futuros)

### Tareas Asíncronas Propuestas

Implementación futura con Celery + Redis/RabbitMQ.

**Tareas propuestas:**

1. **Envío de Emails**

   - Confirmación de pedidos
   - Notificaciones de envío
   - Recuperación de carritos abandonados

2. **Generación de Reportes**

   - Reportes de ventas
   - Análisis de inventario
   - Estadísticas de usuarios

3. **Mantenimiento**
   - Limpieza de sesiones expiradas
   - Sincronización de stock
   - Backup de imágenes

---

## Monitoreo y Logging

### Niveles de Logging

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG: Información detallada de desarrollo
logger.debug(f"Carrito actualizado: {carrito_dict}")

# INFO: Confirmación de operaciones normales
logger.info(f"Producto creado: {producto.nombre}")

# WARNING: Situaciones inesperadas pero manejables
logger.warning(f"Stock bajo para producto {producto_id}")

# ERROR: Errores que impiden operaciones
logger.error(f"Error al subir imagen: {str(e)}")

# CRITICAL: Errores graves del sistema
logger.critical("Database connection lost")
```

### Puntos de Monitoreo

1. **Request/Response Times**
2. **Database Query Performance**
3. **Error Rates**
4. **Session Storage Usage**
5. **External API Calls (Spaces, Transbank)**

---

---

## 📊 Índice de Diagramas

📄 **[Ver índice completo de diagramas de esta vista](./DIAGRAMAS.md)**

El índice contiene enlaces directos a todos los 10 diagramas de proceso con descripciones detalladas.

---

## Conclusión

La Vista de Proceso proporciona una comprensión completa del comportamiento dinámico del sistema, mostrando cómo los diferentes componentes interactúan en tiempo de ejecución para proporcionar la funcionalidad del eCommerce.

**Aspectos Clave:**

- Arquitectura de múltiples workers para concurrencia
- Transacciones ACID para integridad de datos
- Session-based cart storage
- Integración con servicios externos
- Flujos de trabajo claros y bien definidos
- Control de concurrencia con row-level locks
