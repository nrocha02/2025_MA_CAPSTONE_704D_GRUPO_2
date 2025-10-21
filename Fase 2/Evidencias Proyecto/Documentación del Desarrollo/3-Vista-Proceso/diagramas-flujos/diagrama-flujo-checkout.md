# Flujo de Checkout y Pago

Este diagrama muestra el proceso completo de checkout, incluyendo la creación del pedido y la integración con Transbank.

```mermaid
sequenceDiagram
    actor Cliente
    participant Browser
    participant Django
    participant Session
    participant DB
    participant Transbank

    Cliente->>Browser: Click "Finalizar compra"
    Browser->>Django: GET /checkout/
    Django->>Session: Obtener carrito
    Session-->>Django: Items del carrito
    Django-->>Browser: Formulario de datos

    Cliente->>Browser: Completa datos
    Browser->>Django: POST /checkout/procesar/

    Django->>DB: BEGIN TRANSACTION

    alt Cliente registrado
        Django->>DB: SELECT cliente_persona
    else Cliente invitado
        Django->>DB: INSERT INTO sesion_invitado
    end

    Django->>DB: INSERT INTO pedido
    DB-->>Django: pedido_id

    loop Para cada item del carrito
        Django->>DB: INSERT INTO pedido_item
        Django->>DB: UPDATE producto SET stock = stock - cantidad
        Django->>DB: INSERT INTO movimiento_stock
    end

    Django->>Transbank: Iniciar transacción
    Transbank-->>Django: Token de pago

    Django->>DB: INSERT INTO pago (estado='pendiente')
    Django->>DB: COMMIT TRANSACTION

    Django->>Session: Limpiar carrito
    Django-->>Browser: Redirect a Transbank
    Browser->>Transbank: Procesar pago

    Transbank-->>Browser: Resultado pago
    Browser->>Django: GET /checkout/retorno/?token=XXX

    Django->>Transbank: Confirmar transacción
    Transbank-->>Django: Estado de pago

    Django->>DB: UPDATE pago SET estado='aprobado'
    Django->>DB: UPDATE pedido SET estado='Pagado'
    Django->>DB: INSERT INTO pedido_registro

    alt Pago exitoso
        Django->>DB: INSERT INTO documento_tributario
        Django-->>Browser: Página de confirmación
    else Pago rechazado
        Django->>DB: Revertir stock
        Django-->>Browser: Página de error
    end
```

## Fases del Checkout

### Fase 1: Preparación

- Validación de carrito
- Formulario de datos de cliente

### Fase 2: Creación del Pedido

- **Transacción ACID**: Todo o nada
- Actualización de stock con locks
- Registro de movimientos

### Fase 3: Procesamiento de Pago

- Integración con Transbank API
- Redirect a pasarela de pago
- Manejo de callback

### Fase 4: Confirmación

- Actualización de estados
- Generación de documento tributario
- Limpieza de carrito

## Manejo de Errores

- **Stock insuficiente**: Rollback de transacción
- **Pago rechazado**: Reversión de stock
- **Timeout**: Pedido marcado como cancelado
