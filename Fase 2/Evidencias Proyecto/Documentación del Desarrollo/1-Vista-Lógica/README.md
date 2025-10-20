# Vista Lógica

## Descripción General

La Vista Lógica describe la funcionalidad que el sistema proporciona a los usuarios finales. Se centra en la estructura de las abstracciones clave del sistema y sus relaciones.

## Propósito

Esta vista permite entender:

- Las principales entidades del dominio
- Las relaciones entre componentes funcionales
- La organización lógica del sistema
- Los subsistemas y sus responsabilidades

## Contenido

1. [Diagrama de Componentes Principales](#diagrama-de-componentes-principales)
2. [Modelo de Dominio](#modelo-de-dominio)
3. [Diagrama de Clases Principal](#diagrama-de-clases-principal)
4. [Subsistemas Funcionales](#subsistemas-funcionales)

---

## Diagrama de Componentes Principales

📄 **[Ver diagrama completo](./diagrama-componentes-principales.md)**

Este diagrama muestra los componentes principales del sistema y cómo interactúan entre sí.

**Componentes principales:**

- Capa de Presentación (UI Web, Dashboard Admin)
- Capa de Aplicación Django (Ventas, Carrito, Dashboard, Checkout)
- Capa de Dominio (Gestión de Productos, Clientes, Pedidos, Inventario)
- Capa de Infraestructura (PostgreSQL, DigitalOcean Spaces, Transbank API)

---

## Modelo de Dominio

📄 **[Ver diagrama completo](./diagrama-modelo-dominio.md)**

El modelo de dominio representa las entidades principales del negocio y sus relaciones.

**Entidades principales:**

- **Productos**: Producto, Categoría, Marca
- **Clientes**: ClientePersona, ClienteEmpresa, SesionInvitado
- **Pedidos**: Pedido, PedidoItem, Pago, DocumentoTributario

**Relaciones clave:**

- Producto pertenece a una Categoría y opcionalmente a una Marca
- Pedido contiene múltiples PedidoItems
- Pedido es realizado por exactamente un tipo de cliente (XOR)
- Pedido puede tener múltiples Pagos y genera un DocumentoTributario

---

## Diagrama de Clases Principal

📄 **[Ver diagrama completo](./diagrama-clases-principal.md)**

Diagrama detallado de las clases principales del sistema con atributos y métodos.

**Clases principales:**

- **Producto**: Gestión de productos con stock, precio, imágenes
- **Categoria**: Categorías jerárquicas de 2 niveles
- **Marca**: Marcas de productos
- **Carrito**: Gestión de sesión del carrito de compras
- **Pedido**: Gestión de pedidos con estados
- **PedidoItem**: Items individuales de cada pedido
- **MovimientoStock**: Registro de movimientos de inventario

---

## Subsistemas Funcionales

📄 **[Ver todos los diagramas de subsistemas](./diagrama-subsistemas.md)**

### 1. Subsistema de Gestión de Productos

**Responsabilidades:**

- Mantenimiento del catálogo de productos
- Gestión de categorías jerárquicas
- Gestión de marcas
- Control de inventario y stock
- Almacenamiento y gestión de imágenes

**Componentes:**

- `Producto`, `Categoria`, `Marca`
- `MovimientoStock`, `MovimientoEstado`
- Módulo de almacenamiento (DigitalOcean Spaces)

### 2. Subsistema de Ventas

**Responsabilidades:**

- Presentación del catálogo público
- Búsqueda y filtrado de productos
- Visualización de detalles de productos
- Navegación por categorías

**Componentes:**

- Vistas de catálogo
- Sistema de filtros
- Templates de presentación

### 3. Subsistema de Carrito

**Responsabilidades:**

- Gestión temporal del carrito de compras
- Cálculo de totales
- Mantenimiento de estado en sesión
- Validación de stock disponible

**Componentes:**

- Clase `Carrito`
- Context processor
- Vistas de gestión de carrito

### 4. Subsistema de Pedidos

**Responsabilidades:**

- Creación y gestión de pedidos
- Seguimiento de estados de pedidos
- Generación de documentos tributarios
- Registro de cambios de estado

**Componentes:**

- `Pedido`, `PedidoItem`
- `DocumentoTributario`
- `PedidoRegistro`

### 5. Subsistema de Clientes

**Responsabilidades:**

- Gestión de diferentes tipos de clientes
- Mantenimiento de direcciones
- Gestión de métodos de pago
- Sesiones de invitados

**Componentes:**

- `ClientePersona`, `ClienteEmpresa`, `SesionInvitado`
- `Direccion`
- `MetodoPago`

---

## Patrones de Diseño Aplicados

### 1. MTV (Model-Template-View)

Django implementa su propia variación del patrón MVC, llamada MTV.

### 2. Repository Pattern

Los modelos de Django actúan como repositorios, encapsulando el acceso a datos.

### 3. Session State Pattern

El carrito utiliza sesiones para mantener estado temporal.

### 4. Strategy Pattern

Diferentes tipos de clientes (Persona, Empresa, Invitado) implementados como estrategias.

### 5. Observer Pattern

Los registros de movimientos de stock y cambios de estado actúan como observadores.

---

## Restricciones y Reglas de Negocio

1. **Productos:**

   - El precio debe ser mayor o igual a 0
   - El stock debe ser mayor o igual a 0
   - El SKU debe ser único
   - Los slugs deben ser únicos

2. **Categorías:**

   - Máximo 2 niveles de jerarquía
   - Nivel 1: Categorías principales (sin padre)
   - Nivel 2: Subcategorías (con padre)
   - Nombre único por nivel de padre

3. **Pedidos:**

   - Debe tener exactamente un tipo de cliente (XOR)
   - El total debe ser mayor o igual a 0
   - Los items deben tener cantidad > 0

4. **Clientes:**

   - Email único por tipo de cliente
   - RUT único para personas y empresas

5. **Carrito:**
   - No puede exceder stock disponible
   - Costo de envío fijo: $2,990

---

## Conclusión

La Vista Lógica proporciona una comprensión clara de la estructura funcional del sistema, mostrando cómo los diferentes subsistemas trabajan juntos para proporcionar la funcionalidad de un eCommerce completo especializado en productos para mascotas.
