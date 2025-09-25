from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt
import pytz

db = SQLAlchemy()

# Zona horaria de Perú
PERU_TZ = pytz.timezone('America/Lima')

def get_local_datetime():
    """Obtiene la fecha y hora actual en zona horaria de Perú"""
    utc_now = datetime.utcnow()
    utc_now = pytz.utc.localize(utc_now)
    return utc_now.astimezone(PERU_TZ).replace(tzinfo=None)

class Rol(db.Model):
    __tablename__ = 'roles'
    
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relación con usuarios
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)
    
    def __repr__(self):
        return f'<Rol {self.nombre}>'

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    
    # Relación con pedidos como cliente
    pedidos = db.relationship('Pedido', foreign_keys='Pedido.id_usuario', backref='usuario', lazy=True)
    
    def get_id(self):
        return str(self.id_usuario)
    
    def set_password(self, password):
        """Hashea la contraseña usando bcrypt"""
        self.contrasena = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return bcrypt.checkpw(password.encode('utf-8'), self.contrasena.encode('utf-8'))
    
    def is_admin(self):
        return self.rol.nombre.lower() == 'admin'
    
    def is_cliente(self):
        return self.rol.nombre.lower() == 'cliente'
    
    def is_repartidor(self):
        return self.rol.nombre.lower() == 'repartidor'
    
    def is_repartidor(self):
        return self.rol.nombre.lower() == 'repartidor'
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relación con productos
    productos = db.relationship('Producto', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    imagen_url = db.Column(db.String(500))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)
    
    # Relación con detalles de pedido
    detalles_pedido = db.relationship('PedidoDetalle', backref='producto', lazy=True)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    repartidor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    es_delivery = db.Column(db.Boolean, default=False)
    estado = db.Column(db.Enum('pendiente', 'confirmado', 'en_preparacion', 'en_camino', 'entregado', 'cancelado'), 
                      default='pendiente')
    fecha = db.Column(db.DateTime, default=get_local_datetime)
    
    # Relaciones
    detalles = db.relationship('PedidoDetalle', backref='pedido', lazy=True, cascade='all, delete-orphan')
    repartidor = db.relationship('Usuario', foreign_keys=[repartidor_id], backref='pedidos_como_repartidor')
    
    def calcular_total(self):
        """Calcula el total del pedido basado en los detalles"""
        total = sum(detalle.cantidad * detalle.precio_unitario for detalle in self.detalles)
        self.total = total
        return total
    
    def __repr__(self):
        return f'<Pedido {self.id_pedido}>'

class PedidoDetalle(db.Model):
    __tablename__ = 'pedido_detalle'
    
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def __repr__(self):
        return f'<PedidoDetalle {self.id_detalle}>'