-- ============================================
-- SCRIPT CREACIÓN DE TABLAS ECOMMERCE CORDILLERA PETS - POSTGRESQL
-- ============================================

DROP TABLE IF EXISTS documento_tributario, pedido_registro, pago, pedido_item, pedido,
metodo_pago, direccion,
cliente_persona, cliente_empresa, sesion_invitado,
producto, categoria, movimiento_stock, movimiento_estado,
vendedor, sucursal, usuario_admin CASCADE;

CREATE TYPE tipo_metodo_pago AS ENUM ('tarjeta_credito', 'tarjeta_debito', 'cuenta_corriente');
CREATE TYPE estado_metodo AS ENUM ('activo', 'inactivo', 'vencido');
CREATE TYPE estado_sesion AS ENUM ('activa', 'convertida', 'expirada');
CREATE TYPE estado_producto AS ENUM ('activo', 'inactivo', 'eliminado');
CREATE TYPE tipo_operacion AS ENUM ('venta', 'ingreso', 'ajuste', 'devolucion', 'merma');
CREATE TYPE estado_pedido AS ENUM ('Pendiente de pago', 'Procesando', 'Despachado', 'Entregado',
                                   'Entrega fallida', 'Cancelado', 'Reembolsado');
CREATE TYPE tipo_documento AS ENUM ('boleta', 'factura');

-- ============================================
-- TABLAS DE CLIENTES
-- ============================================

CREATE TABLE cliente_persona (
    cliente_persona_id SERIAL PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    nombres VARCHAR(25) NOT NULL,
    apellido_paterno VARCHAR(25) NOT NULL,
    apellido_materno VARCHAR(25) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado BOOLEAN DEFAULT TRUE NOT NULL
);

CREATE TABLE cliente_empresa (
    cliente_empresa_id SERIAL PRIMARY KEY,
    rut_empresa VARCHAR(12) UNIQUE NOT NULL,
    razon_social VARCHAR(100) NOT NULL,
    giro VARCHAR(50) NOT NULL,
    email_contacto VARCHAR(50) UNIQUE NOT NULL,
    telefono_contacto VARCHAR(20) NOT NULL,
    representante_legal VARCHAR(50) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado BOOLEAN DEFAULT TRUE NOT NULL
);

-- ============================================
-- TABLAS DE MÉTODOS DE PAGO
-- ============================================

CREATE TABLE metodo_pago (
    metodo_pago_id SERIAL PRIMARY KEY,
    cliente_persona_id INTEGER NULL,
    cliente_empresa_id INTEGER NULL,
    tipo_metodo tipo_metodo_pago NOT NULL,
    token_seguro VARCHAR(50) NOT NULL,
    ultimos_4_digitos VARCHAR(4) NOT NULL,
    nombre_titular VARCHAR(50) NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    estado estado_metodo DEFAULT 'activo' NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_metodo_pago_cliente_persona
        FOREIGN KEY (cliente_persona_id)
        REFERENCES cliente_persona(cliente_persona_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_metodo_pago_cliente_empresa
        FOREIGN KEY (cliente_empresa_id)
        REFERENCES cliente_empresa(cliente_empresa_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_cliente_unico CHECK (
        (cliente_persona_id IS NOT NULL AND cliente_empresa_id IS NULL) OR
        (cliente_persona_id IS NULL AND cliente_empresa_id IS NOT NULL)
    )
);

-- ============================================
-- TABLAS DE DIRECCIONES
-- ============================================

CREATE TABLE direccion (
    direccion_id SERIAL PRIMARY KEY,
    cliente_persona_id INTEGER NULL,
    cliente_empresa_id INTEGER NULL,
    calle VARCHAR(50) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    codigo_postal SMALLINT NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    CONSTRAINT fk_direccion_cliente_persona
        FOREIGN KEY (cliente_persona_id)
        REFERENCES cliente_persona(cliente_persona_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_direccion_cliente_empresa
        FOREIGN KEY (cliente_empresa_id)
        REFERENCES cliente_empresa(cliente_empresa_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_direccion_cliente_unico CHECK (
        (cliente_persona_id IS NOT NULL AND cliente_empresa_id IS NULL) OR
        (cliente_persona_id IS NULL AND cliente_empresa_id IS NOT NULL)
    )
);

-- ============================================
-- TABLAS DE SESIÓN INVITADO
-- ============================================

CREATE TABLE sesion_invitado (
    cliente_invitado_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    nombres VARCHAR(25) NOT NULL,
    apellido_paterno VARCHAR(25) NOT NULL,
    apellido_materno VARCHAR(25),
    email VARCHAR(50) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    calle_envio VARCHAR(50) NOT NULL,
    ciudad_envio VARCHAR(50) NOT NULL,
    region_envio VARCHAR(50) NOT NULL,
    codigo_postal_envio SMALLINT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado estado_sesion DEFAULT 'activa' NOT NULL
);

-- ============================================
-- TABLAS DE PRODUCTOS Y MOVIMIENTOS
-- ============================================

CREATE TABLE categoria (
    categoria_id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE producto (
    producto_id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    precio INTEGER NOT NULL CHECK (precio >= 0),
    stock INTEGER DEFAULT 0 NOT NULL CHECK (stock >= 0),
    imagen_url TEXT,
    fecha_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado_producto estado_producto DEFAULT 'activo' NOT NULL,
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (categoria_id)
        REFERENCES categoria(categoria_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE movimiento_stock (
    movimiento_stock_id BIGSERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tipo_operacion tipo_operacion NOT NULL,
    CONSTRAINT fk_movimiento_stock_producto
        FOREIGN KEY (producto_id)
        REFERENCES producto(producto_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE movimiento_estado (
    movimiento_estado_id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado_anterior estado_producto NOT NULL,
    estado_actual estado_producto NOT NULL,
    CONSTRAINT fk_movimiento_estado_producto
        FOREIGN KEY (producto_id)
        REFERENCES producto(producto_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_cambio_estado CHECK (estado_anterior != estado_actual)
);

-- ============================================
-- TABLAS DE PEDIDOS Y PAGO
-- ============================================

CREATE TABLE pedido (
    pedido_id BIGSERIAL PRIMARY KEY,
    cliente_persona_id INTEGER NULL,
    cliente_empresa_id INTEGER NULL,
    cliente_invitado_id INTEGER NULL,
    calle VARCHAR(50) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    codigo_postal SMALLINT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado estado_pedido DEFAULT 'Pendiente de pago' NOT NULL,
    total INTEGER NOT NULL CHECK (total >= 0),
    notas TEXT,
    tracking_codigo VARCHAR(50),
    CONSTRAINT fk_pedido_cliente_persona
        FOREIGN KEY (cliente_persona_id)
        REFERENCES cliente_persona(cliente_persona_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pedido_cliente_empresa
        FOREIGN KEY (cliente_empresa_id)
        REFERENCES cliente_empresa(cliente_empresa_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pedido_sesion_invitado
        FOREIGN KEY (cliente_invitado_id)
        REFERENCES sesion_invitado(cliente_invitado_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_pedido_cliente_unico CHECK (
        (cliente_persona_id IS NOT NULL AND cliente_empresa_id IS NULL AND cliente_invitado_id IS NULL) OR
        (cliente_persona_id IS NULL AND cliente_empresa_id IS NOT NULL AND cliente_invitado_id IS NULL) OR
        (cliente_persona_id IS NULL AND cliente_empresa_id IS NULL AND cliente_invitado_id IS NOT NULL)
    )
);

CREATE TABLE pedido_registro (
    registro_id BIGSERIAL PRIMARY KEY,
    pedido_id BIGINT NOT NULL,
    fecha_registro DATE DEFAULT CURRENT_DATE NOT NULL,
    estado_anterior estado_pedido NOT NULL,
    estado_actual estado_pedido NOT NULL,
    CONSTRAINT fk_pedido_registro_pedido
        FOREIGN KEY (pedido_id)
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_cambio_estado_pedido CHECK (estado_anterior != estado_actual)
);

CREATE TABLE pago (
    pago_id BIGSERIAL PRIMARY KEY,
    pedido_id BIGINT NOT NULL,
    monto INTEGER NOT NULL CHECK (monto > 0),
    metodo VARCHAR(50) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    transbank_token VARCHAR(50),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_pago_pedido
        FOREIGN KEY (pedido_id)
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE pedido_item (
    pedido_item_id BIGSERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    pedido_id BIGINT NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario INTEGER NOT NULL CHECK (precio_unitario >= 0),
    subtotal INTEGER NOT NULL CHECK (subtotal >= 0),
    CONSTRAINT fk_pedido_item_producto
        FOREIGN KEY (producto_id)
        REFERENCES producto(producto_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pedido_item_pedido
        FOREIGN KEY (pedido_id)
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE documento_tributario (
    documento_id BIGSERIAL PRIMARY KEY,
    pedido_id BIGINT UNIQUE NOT NULL,
    tipo_documento tipo_documento NOT NULL,
    folio INTEGER,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    subtotal INTEGER NOT NULL CHECK (subtotal >= 0),
    total INTEGER NOT NULL CHECK (total >= 0),
    -- Campos solo para boletas
    rut_cliente VARCHAR(12) NULL,
    nombre_cliente VARCHAR(45) NULL,
    -- Campos solo para facturas
    rut_empresa VARCHAR(12) NULL,
    razon_social VARCHAR(100) NULL,
    giro VARCHAR(255) NULL,
    direccion_facturacion TEXT NULL,
    CONSTRAINT fk_documento_pedido
        FOREIGN KEY (pedido_id)
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_boleta_campos CHECK (
        tipo_documento != 'boleta' OR (rut_cliente IS NOT NULL AND nombre_cliente IS NOT NULL)
    ),
    CONSTRAINT chk_factura_campos CHECK (
        tipo_documento != 'factura' OR (rut_empresa IS NOT NULL AND razon_social IS NOT NULL AND giro IS NOT NULL)
    )
);

-- ============================================
-- TABLAS DE USUARIOS INTERNOS
-- ============================================

CREATE TABLE usuario_admin (
    admin_id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'admin'
);

CREATE TABLE sucursal (
    sucursal_id SERIAL PRIMARY KEY,
    admin_responsable_id INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    direccion TEXT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(50),
    estado BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_sucursal_admin
        FOREIGN KEY (admin_responsable_id)
        REFERENCES usuario_admin(admin_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE vendedor (
    vendedor_id SERIAL PRIMARY KEY,
    sucursal_id INTEGER NOT NULL,
    nombres VARCHAR(25) NOT NULL,
    apellido_paterno VARCHAR(25) NOT NULL,
    apellido_materno VARCHAR(25),
    email VARCHAR(50) UNIQUE NOT NULL,
    telefono VARCHAR(10),
    estado BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_vendedor_sucursal
        FOREIGN KEY (sucursal_id)
        REFERENCES sucursal(sucursal_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================
-- ÍNDICES
-- ============================================

CREATE INDEX idx_cliente_persona_email ON cliente_persona(email);
CREATE INDEX idx_cliente_empresa_email ON cliente_empresa(email_contacto);
CREATE INDEX idx_producto_sku ON producto(sku);
CREATE INDEX idx_producto_categoria ON producto(categoria_id);
CREATE INDEX idx_pedido_fecha ON pedido(fecha);
CREATE INDEX idx_pedido_estado ON pedido(estado);
CREATE INDEX idx_pedido_cliente_persona ON pedido(cliente_persona_id);
CREATE INDEX idx_pedido_cliente_empresa ON pedido(cliente_empresa_id);
CREATE INDEX idx_pedido_cliente_invitado ON pedido(cliente_invitado_id);
CREATE INDEX idx_movimiento_stock_fecha ON movimiento_stock(fecha_movimiento);
CREATE INDEX idx_movimiento_stock_producto ON movimiento_stock(producto_id);
CREATE INDEX idx_pago_pedido ON pago(pedido_id);
CREATE INDEX idx_documento_pedido ON documento_tributario(pedido_id);

-- ============================================
-- COMENTARIOS EN TABLAS Y COLUMNAS
-- ============================================

COMMENT ON TABLE cliente_persona IS 'Tabla de clientes personas naturales';
COMMENT ON TABLE cliente_empresa IS 'Tabla de clientes empresas';
COMMENT ON TABLE producto IS 'Catálogo de productos de la tienda';
COMMENT ON TABLE pedido IS 'Registro de pedidos realizados';
COMMENT ON TABLE documento_tributario IS 'Documentos tributarios (boletas y facturas)';

COMMENT ON COLUMN producto.precio IS 'Precio en pesos chilenos sin decimales';
COMMENT ON COLUMN pedido.total IS 'Total del pedido en pesos chilenos';
COMMENT ON COLUMN documento_tributario.subtotal IS 'Subtotal antes de impuestos';
COMMENT ON COLUMN documento_tributario.total IS 'Total con impuestos incluidos';
COMMENT ON COLUMN usuario_admin.password_hash IS 'Hash de contraseña usando algoritmo seguro (bcrypt, scrypt, etc.)';
