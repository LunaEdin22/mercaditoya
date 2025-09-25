from flask import Flask
from flask_login import LoginManager
from instance.config import Config
from app.models import db, Usuario
import os

def create_app():
    # Configurar el directorio de templates
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views'))
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Importar y registrar blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.usuarios_controller import usuarios_bp
    from app.controllers.productos_controller import productos_bp
    from app.controllers.pedidos_controller import pedidos_bp
    from app.controllers.main_controller import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(main_bp)
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
        # Crear roles por defecto si no existen
        crear_roles_por_defecto()
    
    return app

def crear_roles_por_defecto():
    """Crea los roles por defecto si no existen"""
    from app.models import Rol
    
    roles = ['admin', 'cliente', 'repartidor']
    
    for nombre_rol in roles:
        rol_existente = Rol.query.filter_by(nombre=nombre_rol).first()
        if not rol_existente:
            nuevo_rol = Rol(nombre=nombre_rol)
            db.session.add(nuevo_rol)
    
    db.session.commit()