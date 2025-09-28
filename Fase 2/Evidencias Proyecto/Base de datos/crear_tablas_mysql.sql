-- ============================================
-- SCRIPT CREACIÓN DE TABLAS ECOMMERCE CORDILLERA PETS
-- ============================================

-- Eliminar tablas si existen
DROP TABLE IF EXISTS documento_tributario, pedido_registro, pago, pedido_item, pedido,
metodo_pago, direccion,
cliente_persona, cliente_empresa, sesion_invitado,
producto, categoria, movimiento_stock, movimiento_estado,
vendedor, sucursal, usuario_admin CASCADE;

-- ============================================
-- TABLAS DE CLIENTES
-- ============================================

CREATE TABLE cliente_persona (
    cliente_persona_id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) UNIQUE,
    nombres VARCHAR(25),
    apellido_paterno VARCHAR(25),
    apellido_materno VARCHAR(25),
    email VARCHAR(50) UNIQUE,
    telefono VARCHAR(10),
    fecha_nacimiento DATE,
    fecha_registro TIMESTAMP,
    estado BOOLEAN
);

CREATE TABLE cliente_empresa (
    cliente_empresa_id INT AUTO_INCREMENT PRIMARY KEY,
    rut_empresa VARCHAR(12) UNIQUE,
    razon_social VARCHAR(100),
    giro VARCHAR(50),
    email_contacto VARCHAR(50) UNIQUE,
    telefono_contacto VARCHAR(20),
    representante_legal VARCHAR(50),
    fecha_registro TIMESTAMP,
    estado BOOLEAN
);

-- ============================================
-- TABLAS DE MÉTODOS DE PAGO
-- ============================================

CREATE TABLE metodo_pago (
    metodo_pago_id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_persona_id INT NULL,
    cliente_empresa_id INT NULL,
    tipo_metodo ENUM('tarjeta_credito', 'tarjeta_debito', 'cuenta_corriente'),
    token_seguro VARCHAR(50),
    ultimos_4_digitos VARCHAR(4),
    nombre_titular VARCHAR(50),
    fecha_vencimiento DATE,
    estado ENUM('activo','inactivo','vencido') DEFAULT 'activo',
    fecha_creacion TIMESTAMP,
    CONSTRAINT fk_metodo_pago_cliente_persona 
        FOREIGN KEY (cliente_persona_id) 
        REFERENCES cliente_persona(cliente_persona_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_metodo_pago_cliente_empresa 
        FOREIGN KEY (cliente_empresa_id) 
        REFERENCES cliente_empresa(cliente_empresa_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================
-- TABLAS DE DIRECCIONES
-- ============================================

CREATE TABLE direccion (
    direccion_id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_persona_id INT NULL,
    cliente_empresa_id INT NULL,
    calle VARCHAR(50),
    ciudad VARCHAR(50),
    region VARCHAR(50),
    codigo_postal VARCHAR(20),
    telefono VARCHAR(10),
    CONSTRAINT fk_direccion_cliente_persona 
        FOREIGN KEY (cliente_persona_id) 
        REFERENCES cliente_persona(cliente_persona_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_direccion_cliente_empresa 
        FOREIGN KEY (cliente_empresa_id) 
        REFERENCES cliente_empresa(cliente_empresa_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================
-- TABLAS DE SESIÓN INVITADO
-- ============================================

CREATE TABLE sesion_invitado (
    cliente_invitado_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    nombres VARCHAR(25),
    apellido_paterno VARCHAR(25),
    apellido_materno VARCHAR(25),
    email VARCHAR(50) NOT NULL,
    telefono VARCHAR(10),
    calle_envio VARCHAR(50),
    ciudad_envio VARCHAR(50),
    region_envio VARCHAR(50),
    codigo_postal_envio TINYINT,
    fecha_creacion DATETIME,
    estado ENUM('activa','convertida','expirada') DEFAULT 'activa'
);

-- ============================================
-- TABLAS DE PRODUCTOS Y MOVIMIENTOS
-- ============================================

CREATE TABLE categoria (
    categoria_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT
);

CREATE TABLE producto (
    producto_id INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT,
    sku VARCHAR(100) UNIQUE,
    nombre VARCHAR(50),
    descripcion TEXT,
    precio INT,
    stock INT,
    imagen_url TEXT,
    fecha_creation TIMESTAMP,
    estado_producto ENUM('activo','inactivo','eliminado') DEFAULT 'activo',
    CONSTRAINT fk_producto_categoria 
        FOREIGN KEY (categoria_id) 
        REFERENCES categoria(categoria_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE movimiento_stock (
    movimiento_stock_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    cantidad INT NOT NULL,
    fecha_movimiento TIMESTAMP,
    tipo_operacion ENUM('venta','ingreso','ajuste','devolucion','merma'),
    CONSTRAINT fk_movimiento_stock_producto 
        FOREIGN KEY (producto_id) 
        REFERENCES producto(producto_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE movimiento_estado (
    movimiento_estado_id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    fecha_movimiento TIMESTAMP,
    estado_anterior ENUM('activo','inactivo','eliminado'),
    estado_actual ENUM('activo','inactivo','eliminado'),
    CONSTRAINT fk_movimiento_estado_producto 
        FOREIGN KEY (producto_id) 
        REFERENCES producto(producto_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================
-- TABLAS DE PEDIDOS Y PAGO
-- ============================================

CREATE TABLE pedido (
    pedido_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_persona_id INT NULL,
    cliente_empresa_id INT NULL,
    cliente_invitado_id INT NULL,
    calle VARCHAR(50),
    ciudad VARCHAR(50),
    region VARCHAR(50),
    codigo_postal TINYINT,
    fecha TIMESTAMP,
    estado ENUM('Pendiente de pago','Procesando','Despachado','Entregado',
                'Entrega fallida','Cancelado','Reembolsado') DEFAULT 'Pendiente de pago',
    total INT,
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
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE pedido_registro (
    registro_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pedido_id BIGINT,
    fecha_registro DATE,
    estado_anterior ENUM('Pendiente de pago','Procesando','Despachado','Entregado',
                         'Entrega fallida','Cancelado','Reembolsado'),
    estado_actual ENUM('Pendiente de pago','Procesando','Despachado','Entregado',
                       'Entrega fallida','Cancelado','Reembolsado'),
    CONSTRAINT fk_pedido_registro_pedido 
        FOREIGN KEY (pedido_id) 
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE pago (
    pago_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pedido_id BIGINT NOT NULL,
    monto INT,
    metodo VARCHAR(50),
    estado VARCHAR(50),
    transbank_token VARCHAR(50),
    fecha TIMESTAMP,
    CONSTRAINT fk_pago_pedido 
        FOREIGN KEY (pedido_id) 
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE pedido_item (
    pedido_item_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT,
    pedido_id BIGINT,
    cantidad INT NOT NULL,
    precio_unitario INT NOT NULL,
    subtotal INT NOT NULL,
    CONSTRAINT fk_pedido_item_producto 
        FOREIGN KEY (producto_id) 
        REFERENCES producto(producto_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pedido_item_pedido 
        FOREIGN KEY (pedido_id) 
        REFERENCES pedido(pedido_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE documento_tributario (
    documento_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pedido_id BIGINT UNIQUE NOT NULL,
    tipo_documento ENUM('boleta','factura') NOT NULL,
    folio INT,
    fecha_emision TIMESTAMP,
    subtotal INT NOT NULL,
    total INT NOT NULL,
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
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================
-- TABLAS DE USUARIOS INTERNOS
-- ============================================

CREATE TABLE usuario_admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200),
    email VARCHAR(200) UNIQUE,
    password_hash VARCHAR(50),
    rol VARCHAR(50)
);

CREATE TABLE sucursal (
    sucursal_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_responsable_id INT,
    nombre VARCHAR(50) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(50),
    estado BOOLEAN,
    fecha_creacion TIMESTAMP,
    CONSTRAINT fk_sucursal_admin 
        FOREIGN KEY (admin_responsable_id) 
        REFERENCES usuario_admin(admin_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE vendedor (
    vendedor_id INT AUTO_INCREMENT PRIMARY KEY,
    sucursal_id INT,
    nombres VARCHAR(25),
    apellido_paterno VARCHAR(25),
    apellido_materno VARCHAR(25),
    email VARCHAR(50) UNIQUE,
    telefono VARCHAR(10),
    estado BOOLEAN,
    fecha_creacion TIMESTAMP,
    CONSTRAINT fk_vendedor_sucursal 
        FOREIGN KEY (sucursal_id) 
        REFERENCES sucursal(sucursal_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

