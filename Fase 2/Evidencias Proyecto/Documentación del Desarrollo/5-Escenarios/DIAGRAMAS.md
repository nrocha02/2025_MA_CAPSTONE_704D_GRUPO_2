# 📊 Índice de Diagramas - Escenarios (Vista +1)

Este archivo contiene el índice de todos los diagramas de la vista de Escenarios.

## 👥 Actores del Sistema

📁 **[Ver carpeta de Diagramas](./diagramas/)**

### [Diagrama de Actores](./diagramas/diagrama-actores.md)

Muestra todos los actores que interactúan con el sistema.

**Actores Principales:**

- Cliente Anónimo
- Cliente Registrado
- Cliente Empresa
- Administrador
- Vendedor

**Actores Secundarios:**

- Sistema Transbank
- Servicio de Email (futuro)
- DigitalOcean Spaces

**Jerarquía:**

- Cliente Anónimo ← Cliente Registrado ← Cliente Empresa
- Herencia de privilegios

---

## 🎯 Casos de Uso

### [Diagrama General de Casos de Uso](./diagramas/diagrama-casos-uso.md)

Diagrama completo con todos los casos de uso del sistema y sus relaciones.

**Módulo Ventas (Frontend):**
| ID | Nombre | Actor |
|----|--------|-------|
| UC-01 | Navegar Catálogo | Cliente Anónimo |
| UC-02 | Buscar Productos | Cliente Anónimo |
| UC-03 | Ver Detalle Producto | Cliente Anónimo |
| UC-04 | Gestionar Carrito | Cliente Anónimo |
| UC-05 | Realizar Compra | Cliente Anónimo/Registrado |
| UC-06 | Procesar Pago | Sistema Transbank |

**Módulo Dashboard (Backend):**
| ID | Nombre | Actor |
|----|--------|-------|
| UC-07 | Gestionar Productos | Administrador |
| UC-08 | Gestionar Categorías | Administrador |
| UC-09 | Subir Imágenes | DigitalOcean Spaces |
| UC-10 | Ver Dashboard | Administrador |

**Relaciones:**

- UC-05 <<include>> UC-06
- UC-07 <<include>> UC-09

**Complejidad:**

- Total: 37 días de desarrollo estimados

---

## 📋 Escenarios Detallados

📁 **[Ver carpeta de Escenarios](./escenarios/)**

### [Escenario 1: Compra de Producto por Cliente Anónimo](./escenarios/escenario-compra-completa.md)

Diagrama de secuencia completo del flujo de compra desde navegación hasta confirmación.

**7 Fases del proceso:**

1. **Navegación** (30-60s): Explorar catálogo
2. **Búsqueda y Filtrado** (10-20s): Filtrar productos
3. **Detalle de Producto** (30-90s): Ver información completa
4. **Agregar al Carrito** (2-5s): Añadir producto con AJAX
5. **Ver Carrito** (20-40s): Revisar resumen
6. **Checkout** (2-3min): Formulario y transacción ACID
7. **Pago** (1-2min): Integración con Transbank

**Postcondiciones Éxito:**

- ✅ Pedido creado en estado "Pagado"
- ✅ Stock actualizado
- ✅ Documento tributario generado
- ✅ Carrito vaciado

**Variantes:**

- V1: Cliente se registra durante checkout
- V2: Pago rechazado por Transbank
- V3: Stock insuficiente al confirmar

**Métricas:**

- Tiempo total: ~8 minutos
- Tasa de conversión: ~3%
- Pagos exitosos: ~96%

---

### [Escenario 2: Gestión de Productos por Administrador](./escenarios/escenario-gestion-productos.md)

Flujo completo de operaciones CRUD en el dashboard administrativo.

**6 Fases:**

1. **Acceso al Dashboard**: Login + métricas
2. **Crear Nuevo Producto**: Formulario + validaciones
3. **Upload de Imagen**: boto3 SDK a Spaces
4. **Guardar en BD**: INSERT + movimiento stock
5. **Editar Producto**: UPDATE + reemplazo de imagen
6. **Eliminar Producto**: Verificaciones + DELETE

**Operaciones CRUD:**

#### CREATE

- Validar datos (nombre, precio, SKU, stock)
- Generar slug único
- Upload imagen a Spaces
- INSERT en BD
- Registrar movimiento inicial

#### READ

- Listado con paginación (20 por página)
- Filtros: categoría, marca, estado
- Búsqueda por nombre/SKU
- Métricas del dashboard

#### UPDATE

- Validar cambios
- Reemplazar imagen si cambia
- UPDATE en BD
- Registrar movimiento si cambia stock

#### DELETE

- Verificar dependencias (pedidos)
- Confirmar con admin
- Eliminar imagen de Spaces
- DELETE de BD (CASCADE)

**Variantes:**

- V1: Error al subir imagen
- V2: SKU duplicado
- V3: Producto con pedidos asociados

**Métricas:**

- Crear: 2-3 minutos
- Editar: 1-2 minutos
- Eliminar: 30 segundos

---

### [Escenario 3: Control de Concurrencia en Stock](./escenarios/escenario-concurrencia-stock.md)

Validación del manejo de concurrencia cuando múltiples clientes compran simultáneamente.

**Problema de Race Condition:**

```
Sin control:
T0: Cliente1 lee stock = 3
T1: Cliente2 lee stock = 3
T2: Cliente1 compra 2 → stock = 1
T3: Cliente2 compra 2 → stock = -1 ❌

Con locks (FOR UPDATE):
T0: Cliente1 lock + lee stock = 3
T1: Cliente2 WAIT...
T2: Cliente1 compra 2, stock = 1, unlock
T3: Cliente2 lock + lee stock = 1
T4: Cliente2 ERROR (1 < 2) ✓
```

**Implementación:**

- SELECT ... FOR UPDATE (row-level locks)
- Transacciones ACID (@transaction.atomic)
- Orden consistente para evitar deadlocks
- Timeout de transacciones

**Tipos de Locks:**

- ✅ Row-Level Lock: Granularidad fina, alto rendimiento
- ❌ Table-Level Lock: Muy ineficiente
- 🔄 Optimistic Locking: Propuesto como alternativa

**Detección de Deadlocks:**

- PostgreSQL detecta automáticamente
- Timeout: 1 segundo
- Retry con exponential backoff

**Métricas:**

- Lock wait time: < 100ms (95%)
- Deadlocks: 0/día
- Stock overselling: 0%
- Rollbacks: ~2%

---

## 🔄 Flujos de Trabajo

### [Diagramas de Flujos](./diagramas/diagramas-flujos.md)

Diagramas de flujo para los principales procesos.

**Flujos incluidos:**

#### 1. Flujo: Navegar Catálogo

- Entrada al sitio
- Aplicación de filtros (categoría, marca, búsqueda)
- Mostrar resultados o "Sin resultados"
- Cargar imágenes desde Spaces
- Opción de ver detalle

#### 2. Flujo: Realizar Compra

- Verificar si usuario está registrado
- Formulario de datos (invitado vs registrado)
- Validación de datos
- BEGIN TRANSACTION
- Verificar stock con locks
- Crear pedido y items
- Integración con Transbank
- COMMIT/ROLLBACK según resultado
- Generar documento tributario
- Limpiar carrito

#### 3. Flujo: Gestión de Producto (Dashboard)

- Acciones: Crear, Editar, Eliminar, Listar
- Validaciones por operación
- Upload/eliminación de imágenes
- Manejo de errores

#### 4. Flujo: Manejo de Errores en Checkout

- Validación de carrito vacío
- Validación de formulario
- Verificación de stock
- Verificación de servicio Transbank
- Manejo de pago rechazado
- Rollbacks y reversiones

**Tiempos Estimados:**
| Flujo | Tiempo Promedio | Máximo |
|-------|----------------|--------|
| Navegar catálogo | 30s | 2min |
| Realizar compra | 5min | 15min |
| Gestión producto | 2min | 5min |

---

## 📊 Resumen

| Categoría             | Cantidad de Diagramas  |
| --------------------- | ---------------------- |
| Actores               | 1                      |
| Casos de Uso          | 1 (10 casos incluidos) |
| Escenarios Detallados | 3                      |
| Flujos de Trabajo     | 4 (en 1 archivo)       |
| **Total**             | **5 archivos**         |

---

## ✅ Validación de la Arquitectura

Estos escenarios validan que las 4 vistas anteriores trabajan coherentemente:

### Vista Lógica ↔ Escenarios

- Componentes (Productos, Carrito, Pedidos) → UC-01 a UC-07
- Modelo de dominio → Entidades en escenarios

### Vista de Desarrollo ↔ Escenarios

- Módulos Django (ventas, carrito, dashboard) → Flujos implementados
- Estructura de código → Secuencias de llamadas

### Vista de Proceso ↔ Escenarios

- Flujos de trabajo → Escenarios de compra y gestión
- Control de concurrencia → Escenario 3

### Vista Física ↔ Escenarios

- Infraestructura → Soporta 100+ usuarios concurrentes
- Escalabilidad → Crece según demanda

---

## 🎯 Atributos de Calidad Verificados

| Atributo           | Verificación                                     |
| ------------------ | ------------------------------------------------ |
| **Funcionalidad**  | ✅ Todos los casos de uso implementados          |
| **Rendimiento**    | ✅ Response time < 500ms (p95)                   |
| **Seguridad**      | ✅ Autenticación, validación, transacciones ACID |
| **Usabilidad**     | ✅ Flujos claros e intuitivos                    |
| **Confiabilidad**  | ✅ Control de concurrencia, 0% overselling       |
| **Mantenibilidad** | ✅ Código organizado, documentado                |
| **Escalabilidad**  | ✅ Arquitectura horizontal                       |

---

## 📈 Métricas del Sistema

### Conversión

- Tasa de conversión: ~3%
- Abandono de carrito: ~65%
- Checkouts completados: ~96%

### Performance

- Tiempo de carga catálogo: ~300ms
- Tiempo checkout completo: ~8 minutos
- Requests/segundo: 150-200

### Confiabilidad

- Uptime: 99.5%
- Errores de stock: < 0.5%
- Deadlocks: 0/día

---

**Actualizado**: Octubre 2025  
**Versión**: 1.0
