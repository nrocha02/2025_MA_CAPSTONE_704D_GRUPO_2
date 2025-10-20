# Escenario Completo: Compra de Producto por Cliente Anónimo

Este diagrama de secuencia muestra el flujo completo desde que un cliente anónimo accede al sitio hasta que completa una compra exitosa.

```mermaid
sequenceDiagram
    actor Cliente
    participant Browser
    participant Django
    participant DB
    participant Spaces
    participant Transbank

    Note over Cliente,Transbank: Fase 1: Navegación
    Cliente->>Browser: Accede a www.cordillerapets.cl
    Browser->>Django: GET /
    Django->>DB: SELECT productos activos
    DB-->>Django: Lista de productos
    Django-->>Browser: index.html con productos
    Browser->>Spaces: GET imágenes de productos
    Spaces-->>Browser: Imágenes
    Browser-->>Cliente: Muestra página de inicio

    Note over Cliente,Transbank: Fase 2: Búsqueda y Filtrado
    Cliente->>Browser: Navega a catálogo de perros
    Browser->>Django: GET /catalogo/?categoria=perro
    Django->>DB: SELECT productos WHERE categoria='perro'
    DB-->>Django: Productos filtrados
    Django-->>Browser: catalogo.html
    Browser-->>Cliente: Muestra productos de perro

    Note over Cliente,Transbank: Fase 3: Detalle de Producto
    Cliente->>Browser: Click en producto específico
    Browser->>Django: GET /producto/5/
    Django->>DB: SELECT producto WHERE id=5
    Django->>DB: SELECT productos relacionados
    DB-->>Django: Datos del producto
    Django-->>Browser: producto.html
    Browser-->>Cliente: Muestra detalle completo

    Note over Cliente,Transbank: Fase 4: Agregar al Carrito
    Cliente->>Browser: Click "Agregar al carrito" (cantidad: 2)
    Browser->>Django: POST /carrito/agregar/
    Django->>DB: Verificar stock disponible
    DB-->>Django: Stock: 10 unidades
    Django->>Django: Agregar a sesión carrito
    Django-->>Browser: JSON {success: true, total: 2}
    Browser->>Browser: Actualizar contador carrito
    Browser-->>Cliente: Muestra confirmación

    Note over Cliente,Transbank: Fase 5: Ver Carrito
    Cliente->>Browser: Click en icono carrito
    Browser->>Django: GET /carrito/
    Django->>Django: Leer carrito de sesión
    Django->>Django: Calcular totales
    Django-->>Browser: ver_carrito.html
    Browser-->>Cliente: Muestra resumen de compra

    Note over Cliente,Transbank: Fase 6: Checkout
    Cliente->>Browser: Click "Proceder al pago"
    Browser->>Django: GET /checkout/
    Django-->>Browser: Formulario de datos

    Cliente->>Browser: Completa formulario invitado
    Browser->>Django: POST /checkout/procesar/

    Django->>DB: BEGIN TRANSACTION
    Django->>DB: INSERT sesion_invitado
    Django->>DB: INSERT pedido
    Django->>DB: INSERT pedido_items

    loop Para cada producto
        Django->>DB: UPDATE producto SET stock = stock - cantidad
        Django->>DB: INSERT movimiento_stock
    end

    Note over Cliente,Transbank: Fase 7: Pago
    Django->>Transbank: Iniciar transacción
    Transbank-->>Django: Token de pago
    Django->>DB: INSERT pago (estado='pendiente')
    Django->>DB: COMMIT TRANSACTION

    Django->>Django: Limpiar carrito de sesión
    Django-->>Browser: Redirect a Transbank

    Browser->>Transbank: Mostrar formulario de pago
    Cliente->>Transbank: Ingresa datos tarjeta
    Transbank->>Transbank: Procesar pago

    Transbank-->>Browser: Redirect con resultado
    Browser->>Django: GET /checkout/retorno/?token=XXX

    Django->>Transbank: Confirmar transacción
    Transbank-->>Django: Estado: APROBADO

    Django->>DB: UPDATE pago SET estado='aprobado'
    Django->>DB: UPDATE pedido SET estado='Pagado'
    Django->>DB: INSERT pedido_registro
    Django->>DB: INSERT documento_tributario (boleta)

    Django-->>Browser: Página de confirmación
    Browser-->>Cliente: Muestra confirmación + número de pedido
```

## Fases del Proceso

### Fase 1: Navegación (Pasos 1-7)

- **Objetivo**: Cliente explora el catálogo
- **Duración**: 30-60 segundos
- **Operaciones DB**: 1-2 queries
- **Interacción externa**: Carga de imágenes desde Spaces

### Fase 2: Búsqueda y Filtrado (Pasos 8-11)

- **Objetivo**: Cliente filtra productos por categoría
- **Duración**: 10-20 segundos
- **Operaciones DB**: 1 query con filtros
- **UX**: Resultados instantáneos

### Fase 3: Detalle de Producto (Pasos 12-16)

- **Objetivo**: Cliente ve información completa
- **Duración**: 30-90 segundos
- **Operaciones DB**: 2 queries (producto + relacionados)
- **Elementos**: Descripción, precio, stock, imágenes, relacionados

### Fase 4: Agregar al Carrito (Pasos 17-22)

- **Objetivo**: Cliente agrega producto al carrito
- **Duración**: 2-5 segundos
- **Operaciones DB**: 1 query (verificar stock)
- **Almacenamiento**: Sesión Django
- **UX**: Feedback inmediato con AJAX

### Fase 5: Ver Carrito (Pasos 23-27)

- **Objetivo**: Cliente revisa su carrito
- **Duración**: 20-40 segundos
- **Operaciones DB**: 0 (lectura de sesión)
- **Elementos**: Lista de productos, subtotales, envío, total

### Fase 6: Checkout (Pasos 28-37)

- **Objetivo**: Cliente proporciona datos de envío
- **Duración**: 2-3 minutos
- **Operaciones DB**: Múltiples inserts (transacción ACID)
- **Elementos críticos**:
  - Validación de datos
  - Verificación de stock con locks
  - Actualización de inventario

### Fase 7: Pago (Pasos 38-51)

- **Objetivo**: Procesar pago con Transbank
- **Duración**: 1-2 minutos
- **Interacción externa**: API Transbank
- **Seguridad**: Redirect a pasarela segura
- **Resultado**: Confirmación o rechazo

## Postcondiciones

### Compra Exitosa

- ✅ Pedido creado en estado "Pagado"
- ✅ Stock actualizado (descontado)
- ✅ Documento tributario generado (boleta)
- ✅ Carrito vaciado
- ✅ Sesión de invitado registrada
- ✅ Cliente recibe número de pedido

### Compra Rechazada

- ❌ Pedido cancelado
- ✅ Stock revertido
- ✅ Carrito preservado
- ✅ Cliente recibe mensaje de error

## Variantes del Escenario

### V1: Cliente se Registra Durante Checkout

```
Paso 30: En lugar de "Formulario invitado"
    → Cliente elige "Crear cuenta"
    → Django crea ClientePersona
    → Guarda dirección para futuras compras
```

### V2: Pago Rechazado por Transbank

```
Paso 47: Transbank devuelve estado "RECHAZADO"
    → Django UPDATE pago estado='rechazado'
    → Django UPDATE pedido estado='Cancelado'
    → Django revierte stock (suma cantidad)
    → Cliente ve página de error con opciones
```

### V3: Stock Insuficiente al Confirmar

```
Paso 35: Al hacer UPDATE stock con lock
    → Stock actual < cantidad solicitada
    → Django ejecuta ROLLBACK
    → Cliente recibe error "Stock insuficiente"
    → Carrito se mantiene para ajustar cantidad
```

## Métricas del Escenario

| Métrica                  | Valor Objetivo | Valor Actual |
| ------------------------ | -------------- | ------------ |
| Tiempo total             | < 10 minutos   | ~8 minutos   |
| Tasa de conversión       | > 2%           | ~3%          |
| Tasa de abandono carrito | < 70%          | ~65%         |
| Errores de stock         | < 1%           | ~0.5%        |
| Pagos exitosos           | > 95%          | ~96%         |

## Puntos de Mejora Identificados

1. **Fase 4**: Agregar validación de cantidad máxima por producto
2. **Fase 6**: Implementar recuperación de carritos abandonados
3. **Fase 7**: Agregar método de pago alternativo (transferencia)
4. **Post-compra**: Enviar email de confirmación (pendiente)
5. **General**: Implementar tracking de envío
