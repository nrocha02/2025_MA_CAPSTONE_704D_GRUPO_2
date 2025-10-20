# 📊 Índice de Diagramas - Vista de Proceso

Este archivo contiene el índice de todos los diagramas de la Vista de Proceso.

## 🏗️ Arquitectura

### [Arquitectura de Procesos del Sistema](./diagrama-arquitectura-procesos.md)

Muestra la arquitectura completa desde el cliente web hasta los servicios externos, incluyendo workers de Gunicorn y servicios de terceros.

**Componentes principales:**

- Navegador Web (Cliente HTTP)
- Servidor Web (WSGI, Django, Workers)
- Servicios Externos (PostgreSQL, Spaces, Transbank)

---

## 🔄 Flujos de Trabajo

### [Flujo de Navegación del Catálogo](./diagrama-flujo-catalogo.md)

Secuencia completa del proceso de navegación por el catálogo de productos.

**Pasos clave:**

1. Request HTTP a /catalogo/
2. Query a base de datos
3. Aplicación de filtros
4. Carga de imágenes desde Spaces
5. Renderizado de template

### [Flujo de Gestión del Carrito](./diagrama-flujo-carrito.md)

Proceso de agregar productos al carrito con verificación de stock en tiempo real.

**Características:**

- AJAX request asíncrono
- Validación de stock
- Almacenamiento en sesión
- Respuesta JSON

### [Flujo de Creación de Producto](./diagrama-flujo-crear-producto.md)

Proceso completo de creación de productos desde el dashboard administrativo.

**Fases:**

1. Validación de datos
2. Generación de slug
3. Upload de imagen a Spaces
4. Inserción en base de datos
5. Registro de movimiento de stock

### [Flujo de Checkout y Pago](./diagrama-flujo-checkout.md)

Diagrama de secuencia del proceso completo de checkout incluyendo integración con Transbank.

**Componentes involucrados:**

- Cliente, Browser, Django, Session, DB, Transbank
- Transacciones ACID
- Manejo de errores y reversiones

---

## 📝 Diagramas de Secuencia

### [Secuencia: Búsqueda y Filtrado](./diagrama-secuencia-busqueda.md)

Interacción entre capas del sistema (Vista, Controlador, Modelo, Base de Datos) durante búsqueda de productos.

**Patrón MVC:**

- Vista (Browser)
- Controlador (Django View)
- Modelo (ORM)
- Base de Datos (PostgreSQL)

### [Secuencia: Actualización de Carrito](./diagrama-secuencia-actualizar-carrito.md)

Flujo detallado de actualización de cantidad de productos en el carrito.

**Clase Carrito:**

- Inicialización desde sesión
- Operaciones (agregar, actualizar, eliminar)
- Cálculos (subtotales, total, envío)
- Persistencia en sesión

---

## 🔀 Diagramas de Estados

### [Diagramas de Estados](./diagramas-estados.md)

Máquinas de estados para las entidades principales del sistema.

**Estados incluidos:**

#### 1. Estados del Pedido

- Pendiente_Pago → Pagado → En_Preparacion → Enviado → En_Transito → Entregado
- Transiciones de cancelación y devolución

#### 2. Estados del Producto

- Activo ↔ Inactivo
- Activo ↔ Agotado
- Cualquiera → Descontinuado (final)

#### 3. Estados de la Sesión del Carrito

- Vacio ↔ Con_Items ↔ Checkout
- Expiración (24 horas)

---

## ⚡ Concurrencia y Performance

### [Modelo de Concurrencia](./diagrama-concurrencia.md)

Arquitectura de workers y estrategias de optimización de performance.

**Temas cubiertos:**

- Configuración de Gunicorn workers
- Connection pooling a PostgreSQL
- Query optimization (N+1 problem)
- Session storage
- Static files serving

### [Control de Sincronización](./diagrama-sincronizacion.md)

Mecanismos de control de concurrencia para operaciones críticas.

**Técnicas implementadas:**

- Row-level locks (FOR UPDATE)
- Transacciones ACID
- Optimistic locking (propuesto)
- Deadlock detection
- Isolation levels

---

## 📈 Resumen

| Categoría         | Cantidad de Diagramas |
| ----------------- | --------------------- |
| Arquitectura      | 1                     |
| Flujos de Trabajo | 4                     |
| Secuencias        | 2                     |
| Estados           | 3 (en 1 archivo)      |
| Concurrencia      | 2                     |
| **Total**         | **10 archivos**       |

---

## 🎯 Casos de Uso Validados

Estos diagramas validan los siguientes casos de uso:

- ✅ UC-01: Navegar Catálogo
- ✅ UC-02: Buscar Productos
- ✅ UC-03: Ver Detalle Producto
- ✅ UC-04: Gestionar Carrito
- ✅ UC-05: Realizar Compra
- ✅ UC-06: Procesar Pago
- ✅ UC-07: Gestionar Productos

---

## 🔗 Relaciones con Otras Vistas

| Vista                   | Relación                                         |
| ----------------------- | ------------------------------------------------ |
| **Vista Lógica**        | Los procesos implementan los componentes lógicos |
| **Vista de Desarrollo** | Los flujos ejecutan código de los módulos Django |
| **Vista Física**        | Los procesos se despliegan en la infraestructura |
| **Escenarios**          | Los flujos validan los casos de uso              |

---

**Actualizado**: Octubre 2025  
**Versión**: 1.0
