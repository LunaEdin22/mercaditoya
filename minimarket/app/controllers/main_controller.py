from flask import Blueprint, render_template, request
from app.models import Producto, Categoria, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal con productos destacados"""
    # Obtener productos más vendidos o destacados
    productos_destacados = Producto.query.limit(8).all()
    categorias = Categoria.query.all()
    
    return render_template('index.html', 
                         productos=productos_destacados, 
                         categorias=categorias)

@main_bp.route('/productos')
def listar_productos():
    """Lista todos los productos con filtros"""
    categoria_id = request.args.get('categoria', type=int)
    busqueda = request.args.get('q', '')
    
    query = Producto.query
    
    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)
    
    if busqueda:
        query = query.filter(Producto.nombre.contains(busqueda))
    
    productos = query.all()
    categorias = Categoria.query.all()
    
    return render_template('productos.html', 
                         productos=productos, 
                         categorias=categorias,
                         categoria_seleccionada=categoria_id,
                         busqueda=busqueda)

@main_bp.route('/producto/<int:id>')
def detalle_producto(id):
    """Detalle de un producto específico"""
    producto = Producto.query.get_or_404(id)
    productos_relacionados = Producto.query.filter(
        Producto.id_categoria == producto.id_categoria,
        Producto.id_producto != producto.id_producto
    ).limit(4).all()
    
    return render_template('detalle_producto.html', 
                         producto=producto,
                         productos_relacionados=productos_relacionados)