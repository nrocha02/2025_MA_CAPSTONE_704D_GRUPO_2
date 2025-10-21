# Diagramas de Estados - Vista de Proceso

Esta carpeta contiene los diagramas de máquinas de estados del sistema.

## 📂 Diagrama Disponible

**[Diagramas de Estados](./diagramas-estados.md)**

Máquinas de estados para las entidades principales del sistema:

### Estados Incluidos

1. **Estados del Pedido**

   - Pendiente_Pago → Pagado → En_Preparacion → Enviado → En_Transito → Entregado
   - Transiciones de cancelación y devolución

2. **Estados del Producto**

   - Activo ↔ Inactivo
   - Activo ↔ Agotado
   - Cualquiera → Descontinuado (final)

3. **Estados de la Sesión del Carrito**
   - Vacio ↔ Con_Items ↔ Checkout
   - Expiración (24 horas)

## 🔗 Navegación

- [← Volver a Vista de Proceso](../README.md)
- [Ver Índice de Diagramas](../DIAGRAMAS.md)

---

**Actualizado**: Octubre 2025  
**Versión**: 1.0
