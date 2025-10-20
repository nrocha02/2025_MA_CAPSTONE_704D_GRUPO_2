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
4. [Diagrama de Estados](#diagrama-de-estados)
5. [Concurrencia y Performance](#concurrencia-y-performance)

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
