# 📊 Índice de Diagramas - Vista de Proceso

Este archivo contiene el índice de todos los diagramas de la Vista de Proceso.

## 🏗️ Arquitectura

📁 **[Ver carpeta de Diagramas de Arquitectura](./diagramas-arquitectura/)**

### [Arquitectura de Procesos del Sistema](./diagramas-arquitectura/diagrama-arquitectura-procesos.md)

Muestra la arquitectura completa desde el cliente web hasta los servicios externos, incluyendo workers de Gunicorn y servicios de terceros.

**Componentes principales:**

- Navegador Web (Cliente HTTP)
- Servidor Web (WSGI, Django, Workers)
- Servicios Externos (PostgreSQL, Spaces, Transbank)

---

## 🔄 Flujos de Trabajo

📁 **[Ver carpeta de Diagramas de Flujos](./diagramas-flujos/)**

### [Flujo de Navegación del Catálogo](./diagramas-flujos/diagrama-flujo-catalogo.md)

Secuencia completa del proceso de navegación por el catálogo de productos.

**Pasos clave:**

1. Request HTTP a /catalogo/
2. Query a base de datos
3. Aplicación de filtros
4. Carga de imágenes desde Spaces
5. Renderizado de template

### [Flujo de Gestión del Carrito](./diagramas-flujos/diagrama-flujo-carrito.md)

Proceso de agregar productos al carrito con verificación de stock en tiempo real.

**Características:**

- AJAX request asíncrono
- Validación de stock
- Almacenamiento en sesión
- Respuesta JSON

### [Flujo de Creación de Producto](./diagramas-flujos/diagrama-flujo-crear-producto.md)

Proceso completo de creación de productos desde el dashboard administrativo.

**Fases:**

1. Validación de datos
2. Generación de slug
3. Upload de imagen a Spaces
4. Inserción en base de datos
5. Registro de movimiento de stock

### [Flujo de Checkout y Pago](./diagramas-flujos/diagrama-flujo-checkout.md)

Diagrama de secuencia del proceso completo de checkout incluyendo integración con Transbank.

**Componentes involucrados:**

- Cliente, Browser, Django, Session, DB, Transbank
- Transacciones ACID
- Manejo de errores y reversiones

---

## 📝 Diagramas de Secuencia

📁 **[Ver carpeta de Diagramas de Secuencia](./diagramas-secuencia/)**

### [Secuencia: Búsqueda y Filtrado](./diagramas-secuencia/diagrama-secuencia-busqueda.md)

Interacción entre capas del sistema (Vista, Controlador, Modelo, Base de Datos) durante búsqueda de productos.

**Patrón MVC:**

- Vista (Browser)
- Controlador (Django View)
- Modelo (ORM)
- Base de Datos (PostgreSQL)

### [Secuencia: Actualización de Carrito](./diagramas-secuencia/diagrama-secuencia-actualizar-carrito.md)

Flujo detallado de actualización de cantidad de productos en el carrito.

**Clase Carrito:**

- Inicialización desde sesión
- Operaciones (agregar, actualizar, eliminar)
- Cálculos (subtotales, total, envío)
- Persistencia en sesión

---

## 🔀 Diagramas de Estados

📁 **[Ver carpeta de Diagramas de Estados](./diagramas-estados/)**

### [Diagramas de Estados](./diagramas-estados/diagramas-estados.md)

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

📁 **[Ver carpeta de Diagramas de Concurrencia](./diagramas-concurrencia/)**

### [Modelo de Concurrencia](./diagramas-concurrencia/diagrama-concurrencia.md)

Arquitectura de workers y estrategias de optimización de performance.

**Temas cubiertos:**

- Configuración de Gunicorn workers
- Connection pooling a PostgreSQL
- Query optimization (N+1 problem)
- Session storage
- Static files serving

### [Control de Sincronización](./diagramas-concurrencia/diagrama-sincronizacion.md)

Mecanismos de control de concurrencia para operaciones críticas.

**Técnicas implementadas:**

- Row-level locks (FOR UPDATE)
- Transacciones ACID
- Optimistic locking (propuesto)
- Deadlock detection
- Isolation levels

---

---

## 🎬 Diagramas de Actividades

📄 **[Ver carpeta completa de Diagramas de Actividades](./diagramas-actividades/)**

### [Actividad: Proceso de Compra Completa](./diagramas-actividades/diagrama-actividad-compra-completa.md)

Flujo completo de una compra desde la navegación hasta la confirmación del pedido.

**Fases incluidas:**

1. Navegación y Selección de Productos
2. Gestión del Carrito
3. Proceso de Checkout
4. Transacción y Actualización de Stock
5. Procesamiento de Pago con Transbank
6. Confirmación o Reversión

**Puntos de decisión clave:**

- ¿Stock disponible?
- ¿Usuario registrado?
- ¿Datos válidos?
- Resultado del pago (aprobado/rechazado/timeout)

### [Actividad: Gestión de Productos (Dashboard)](./diagramas-actividades/diagrama-actividad-gestion-productos.md)

Flujo de gestión administrativa de productos con operaciones CRUD completas.

**Operaciones incluidas:**

- **Crear**: Validación, generación de slug, upload de imagen, registro en BD
- **Leer**: Listado con filtros y búsqueda
- **Actualizar**: Edición de datos, cambio de imagen, ajuste de stock
- **Eliminar**: Verificación de dependencias, eliminación física

**Integración:**

- DigitalOcean Spaces para manejo de imágenes
- Transacciones ACID para integridad
- Auditoría mediante movimientos de stock

### [Actividad: Autenticación y Registro](./diagramas-actividades/diagrama-actividad-autenticacion.md)

Flujos de seguridad para inicio de sesión, registro de usuarios y recuperación de contraseña.

**Flujos incluidos:**

1. **Inicio de Sesión**: Validación de credenciales, protección contra fuerza bruta
2. **Registro**: Validación de RUT, email, contraseña segura, creación de cuenta
3. **Cerrar Sesión**: Persistencia de carrito, destrucción de sesión
4. **Recuperar Contraseña**: Generación de token, protección contra enumeración

**Seguridad:**

- Hashing de contraseñas (SHA-256)
- Límite de intentos fallidos (5)
- Bloqueo temporal (15 minutos)
- Validación de RUT chileno

### [Actividad: Gestión de Inventario y Stock](./diagramas-actividades/diagrama-actividad-gestion-inventario.md)

Gestión completa de inventario con movimientos, alertas y auditoría.

**Operaciones incluidas:**

- **Consultar Inventario**: Listado con filtros, detección de stock bajo
- **Registrar Ingreso**: Recepción de mercancía
- **Registrar Egreso**: Salidas por devolución, daño, etc.
- **Ajuste de Inventario**: Corrección según conteo físico
- **Ver Historial**: Auditoría de movimientos
- **Configurar Stock Mínimo**: Establecer alertas

**Sistema de Alertas:**

- Stock bajo
- Stock crítico
- Stock agotado
- Discrepancias significativas

### [Actividad: Navegación y Búsqueda en Catálogo](./diagramas-actividades/diagrama-actividad-navegacion-catalogo.md)

Flujo detallado de navegación por el catálogo con búsqueda, filtrado y visualización de productos.

**Flujos incluidos:**

- **Ver Catálogo Completo**: Carga inicial de productos activos
- **Buscar por Texto**: Búsqueda en nombre y descripción (ICONTAINS)
- **Filtrar por Categoría**: Aplicar filtro de categoría
- **Filtrar por Marca**: Aplicar filtro de marca
- **Combinar Filtros**: Múltiples filtros simultáneos
- **Ordenar Resultados**: Por precio, nombre, fecha
- **Ver Detalle de Producto**: Página de producto individual
- **Agregar al Carrito**: AJAX desde detalle de producto

**Optimizaciones:**

- SELECT_RELATED para evitar N+1 queries
- Lazy loading de imágenes
- Caché de categorías y marcas
- Paginación (24 productos por página)

📄 **[Ver resumen completo de diagramas de actividades](./diagramas-actividades/RESUMEN-DIAGRAMAS-ACTIVIDADES.md)**

---

## 📈 Resumen

| Categoría         | Cantidad de Diagramas |
| ----------------- | --------------------- |
| Arquitectura      | 1                     |
| Flujos de Trabajo | 4                     |
| Secuencias        | 2                     |
| Estados           | 3 (en 1 archivo)      |
| Concurrencia      | 2                     |
| **Actividades**   | **5**                 |
| **Total**         | **15 archivos**       |

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
