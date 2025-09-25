
CREATE DATABASE minimarket;
GO
USE minimarket;
GO

CREATE TABLE roles (
    id_rol INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL, 
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    id_rol INT,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

CREATE TABLE categorias (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    imagen_url VARCHAR(500),
    id_categoria INT,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

CREATE TABLE pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT, 
	repartidor_id INT NULL, 
    total DECIMAL(10,2) NOT NULL,
    es_delivery BIT DEFAULT 0,
    estado VARCHAR(50) DEFAULT 'Pendiente',
    fecha DATETIME DEFAULT GETDATE(), 
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
	FOREIGN KEY (repartidor_id) REFERENCES usuarios(id_usuario)

);


CREATE TABLE pedido_detalle (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT,
    id_producto INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- INSERCIONES

-- Roles
INSERT INTO roles (nombre) VALUES
('cliente'),
('admin'),
('repartidor');

-- Usuarios (Contraseña: 123456)
INSERT INTO usuarios (nombre_completo, email, contrasena, telefono, direccion, id_rol) VALUES
('Admin Sistema', 'admin@gmail.com', '$2b$12$MHMkbuqU00xsCGtrqyROnOqpxhYqSeBFQ1d9lAkf1ynb//h.1AYOG', '999888777', 'Oficina Central', 2),
('Juan Cliente', 'juan@gmail.com', '$2b$12$MHMkbuqU00xsCGtrqyROnOqpxhYqSeBFQ1d9lAkf1ynb//h.1AYOG', '987654321', 'Av. Ejemplo 123', 1),
('Manuel Dongo', 'manuel@gmail.com', '$2b$12$MHMkbuqU00xsCGtrqyROnOqpxhYqSeBFQ1d9lAkf1ynb//h.1AYOG', '987654322', 'Jr. Repartidores 100', 3), 
('Brandon Mena', 'brandon@gmail.com', '$2b$12$MHMkbuqU00xsCGtrqyROnOqpxhYqSeBFQ1d9lAkf1ynb//h.1AYOG', '987654323', 'Av. Delivery 200', 3), 
('Edinson Luna', 'luna@gmail.com', '$2b$12$MHMkbuqU00xsCGtrqyROnOqpxhYqSeBFQ1d9lAkf1ynb//h.1AYOG', '987654324', 'Calle Reparto 300', 3),
('Ricardo Mendoza HH', 'ricardo@gmail.com', '$2b$12$MHMkbuqU00xsCGtrqyROnOqpxhYqSeBFQ1d9lAkf1ynb//h.1AYOG', '952486159', 'Los Angeles Mz 15', 1);
-- Categorias
INSERT INTO categorias (nombre) VALUES
('Bebidas'),
('Snacks'),
('Lacteos'),
('Frutas y Verduras'),
('Aseo y Limpieza'),
('Panaderia'),
('Chicles');

-- Productos
INSERT INTO productos (nombre, precio, stock, imagen_url, id_categoria) VALUES
('Coca Cola 1L', 1.50, 20, 'https://i.ibb.co/twrxcy7j/a1d4faa1a939.png', 1),
('Agua Mineral 500ml', 0.80, 50, 'https://i.ibb.co/BV9tk9dr/d35a67880c9d.png', 1),
('Jugo de Naranja 1L', 2.00, 25, 'https://i.ibb.co/QvGbDhcR/5ebb353c021a.png', 1),
('Papas Fritas', 1.20, 30, 'https://i.ibb.co/fYnNdj76/9689cff8efa7.png', 2),
('Galletas Chocolate', 1.00, 40, 'https://i.ibb.co/DnKwP4z/0e12399e6b27.png', 2),
('Jumbo', 0.70, 60, 'https://i.ibb.co/Xft0LGKH/ef3f8e586f34.png', 2),
('Yogur Natural', 0.90, 15, 'https://i.ibb.co/HD8LpcqJ/ff52986dae02.png', 3),
('Leche Entera 1L', 1.10, 35, 'https://i.ibb.co/zTzcb2h7/ad8d060bd4a2.png', 3),
('Manzana Roja', 0.60, 100, 'https://i.ibb.co/DgtnnX5B/46ab5110e8e7.png', 4),
('Platano', 0.40, 80, 'https://i.ibb.co/qL0bY4j8/15f219b69ee8.png', 4),
('Zanahoria (kg)', 0.90, 50, 'https://i.ibb.co/KckjssvQ/ab3f7ea3d180.png', 4),
('Detergente Liquido', 3.50, 20, 'https://i.ibb.co/Kjq82Jq4/60de2387ff2c.png', 5),
('Jabon de Baño', 0.50, 100, 'https://i.ibb.co/TBhJbhH2/72642e9334c2.png', 5),
('Pan Marraqueta (unidad)', 0.20, 200, 'https://i.ibb.co/tPPLY8vL/91dc6774210f.png', 6),
('Croissant', 0.80, 40, 'https://i.ibb.co/cS81vYDp/8f516b5bb18b.png', 6);

