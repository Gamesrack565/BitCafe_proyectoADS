--Creacion mtz 
DROP DATABASE IF EXISTS bitcafe_db;
CREATE DATABASE bitcafe_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bitcafe_db;


CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol ENUM('cliente', 'staff', 'admin') NOT NULL DEFAULT 'cliente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    url_imagen VARCHAR(255) NULL,
    esta_disponible BOOLEAN NOT NULL DEFAULT TRUE,
    maneja_stock BOOLEAN NOT NULL DEFAULT FALSE,
    
    cantidad_stock INT NOT NULL DEFAULT 0,
    
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE carritos (
    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_carrito_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE carrito_items (
    id_item_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    notas VARCHAR(255) NULL,
    
    CONSTRAINT fk_item_carrito
        FOREIGN KEY (id_carrito) REFERENCES carritos(id_carrito)
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    CONSTRAINT fk_item_producto
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        ON DELETE CASCADE ON UPDATE CASCADE,
        
    UNIQUE KEY uq_producto_en_carrito (id_carrito, id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,
    num_orden VARCHAR(20) NOT NULL UNIQUE,
    total_pedido DECIMAL(10, 2) NOT NULL,
    estado_pedido ENUM('pendiente', 'preparacion', 'listo', 'entregado', 'cancelado') NOT NULL DEFAULT 'pendiente',
    metodo_pago ENUM('efectivo', 'transferencia', 'tarjeta') NOT NULL,
    estado_pago ENUM('pendiente', 'pagado') NOT NULL DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_pedido_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE pedido_items (
    id_item_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NULL,
    cantidad INT NOT NULL,
    precio_unitario_compra DECIMAL(10, 2) NOT NULL,
    notas VARCHAR(255) NULL,
    
    CONSTRAINT fk_pitem_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    CONSTRAINT fk_pitem_producto
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tokens_recuperacion (
    id_token INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    tipo_token ENUM('password', 'usuario') NOT NULL,
    fecha_expiracion DATETIME NOT NULL,
    fue_usado BOOLEAN NOT NULL DEFAULT FALSE,
    
    CONSTRAINT fk_token_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE configuracion_sistema (
    clave VARCHAR(50) PRIMARY KEY,
    valor VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;