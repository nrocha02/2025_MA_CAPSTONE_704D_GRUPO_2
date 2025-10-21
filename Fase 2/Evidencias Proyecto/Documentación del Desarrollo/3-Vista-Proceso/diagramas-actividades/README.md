# 📋 Diagramas de Actividades - Vista de Proceso

Este directorio contiene todos los diagramas de actividades del sistema CordilleraPets eCommerce.

## 📂 Contenido

### Diagramas Disponibles

1. **[Proceso de Compra Completa](./diagrama-actividad-compra-completa.md)**

   - Flujo end-to-end desde navegación hasta confirmación
   - Fases: Navegación, Carrito, Checkout, Transacción, Pago, Confirmación
   - Incluye integración con Transbank y manejo de transacciones ACID

2. **[Gestión de Productos (Dashboard)](./diagrama-actividad-gestion-productos.md)**

   - Operaciones CRUD completas
   - Integración con DigitalOcean Spaces
   - Validaciones de negocio y auditoría

3. **[Autenticación y Registro](./diagrama-actividad-autenticacion.md)**

   - Inicio de sesión con protección contra fuerza bruta
   - Registro con validación de RUT chileno
   - Recuperación de contraseña segura

4. **[Gestión de Inventario y Stock](./diagrama-actividad-gestion-inventario.md)**

   - Movimientos de stock (ingresos, egresos, ajustes)
   - Sistema de alertas automatizado
   - Auditoría completa de movimientos

5. **[Navegación y Búsqueda en Catálogo](./diagrama-actividad-navegacion-catalogo.md)**
   - Búsqueda y filtrado de productos
   - Optimizaciones de performance
   - Interacciones AJAX

## 📊 Resumen General

**[Ver Resumen Completo](./RESUMEN-DIAGRAMAS-ACTIVIDADES.md)**

El documento de resumen incluye:

- Descripción detallada de cada diagrama
- Tecnologías y patrones utilizados
- Validaciones y seguridad implementada
- Métricas y KPIs
- Casos de uso validados

## 🎯 Características de los Diagramas

Cada diagrama incluye:

✅ **Diagramas Mermaid** completos y visuales  
✅ **Descripción de actividades** paso a paso  
✅ **Puntos de decisión** con criterios claros  
✅ **Código de ejemplo** (Python/JavaScript)  
✅ **Validaciones** en múltiples niveles  
✅ **Manejo de errores** y casos alternativos  
✅ **Optimizaciones** de performance  
✅ **Métricas y KPIs** de seguimiento  
✅ **Aspectos de seguridad** implementados  
✅ **Auditoría y logs** detallados

## 🔧 Aspectos Técnicos

### Patrones Implementados

- **Transacciones ACID**: `@transaction.atomic`
- **Row-Level Locks**: `SELECT FOR UPDATE`
- **Query Optimization**: `select_related()`, `prefetch_related()`
- **Repository Pattern**: Clase `Carrito`
- **State Machine**: Estados de pedido y producto

### Integraciones

- **DigitalOcean Spaces**: Almacenamiento de imágenes
- **Transbank API**: Procesamiento de pagos
- **Django Auth**: Autenticación y sesiones
- **PostgreSQL**: Base de datos con locks

### Seguridad

- Hashing de contraseñas (SHA-256)
- Protección CSRF
- Límite de intentos de login
- Validación de entrada en todos los niveles
- SQL injection prevention (Django ORM)

## 📈 Estadísticas

| Métrica                | Valor |
| ---------------------- | ----- |
| Total de Diagramas     | 5     |
| Flujos Documentados    | 18+   |
| Puntos de Decisión     | 40+   |
| Validaciones           | 30+   |
| Transacciones ACID     | 8     |
| Integraciones Externas | 2     |

## 🔗 Navegación

- [← Volver a Vista de Proceso](../README.md)
- [Ver Índice de Diagramas](../DIAGRAMAS.md)
- [Ver Resumen de Actividades](./RESUMEN-DIAGRAMAS-ACTIVIDADES.md)

---

**Actualizado**: Octubre 2025  
**Versión**: 1.0  
**Sistema**: CordilleraPets eCommerce
