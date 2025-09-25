from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import requests
import base64
from app.models import Producto, Categoria, db
import os
from PIL import Image
import io

productos_bp = Blueprint('productos', __name__)

# Configuración de formatos de imagen permitidos
ALLOWED_IMAGE_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'avif', 'tiff', 'tif', 'ico'
}

def validar_archivo_imagen(archivo):
    """
    Valida si el archivo es una imagen válida
    Retorna: (es_valido, mensaje_error)
    """
    if not archivo or not archivo.filename:
        return False, "No se seleccionó ningún archivo"
    
    # Verificar extensión
    filename = secure_filename(archivo.filename.lower())
    if '.' not in filename:
        return False, "El archivo debe tener una extensión válida"
    
    extension = filename.rsplit('.', 1)[1]
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        formatos_permitidos = ', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        return False, f"❌ Formato de imagen no permitido. Por favor, use uno de estos formatos: {formatos_permitidos.upper()}"
    
    # Verificar que sea una imagen real usando PIL
    try:
        archivo.seek(0)  # Volver al inicio del archivo
        imagen = Image.open(archivo)
        imagen.verify()  # Verificar que sea una imagen válida
        archivo.seek(0)  # Volver al inicio para uso posterior
        return True, "✅ Archivo de imagen válido"
    except Exception as e:
        return False, f"❌ El archivo no es una imagen válida o está corrupto. Error: {str(e)}"

def optimizar_imagen(archivo, max_width=1200, max_height=1200, quality=85):
    """
    Optimiza la imagen redimensionándola y comprimiéndola
    """
    try:
        archivo.seek(0)
        imagen = Image.open(archivo)
        
        # Convertir a RGB si es necesario (para JPEG)
        if imagen.mode in ('RGBA', 'LA', 'P'):
            rgb_imagen = Image.new('RGB', imagen.size, (255, 255, 255))
            if imagen.mode == 'P':
                imagen = imagen.convert('RGBA')
            rgb_imagen.paste(imagen, mask=imagen.split()[-1] if imagen.mode == 'RGBA' else None)
            imagen = rgb_imagen
        
        # Redimensionar si es necesario
        if imagen.width > max_width or imagen.height > max_height:
            imagen.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Guardar en memoria como JPEG optimizado
        output = io.BytesIO()
        imagen.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"Error al optimizar imagen: {e}")
        archivo.seek(0)
        return archivo

def subir_imagen_imgbb(archivo):
    """
    Sube una imagen a imgbb después de validarla y optimizarla
    Retorna: (url, mensaje_error)
    """
    try:
        # Validar el archivo
        es_valido, mensaje = validar_archivo_imagen(archivo)
        if not es_valido:
            return None, mensaje
        
        # Optimizar la imagen
        archivo_optimizado = optimizar_imagen(archivo)
        
        # Convertir archivo optimizado a base64
        archivo_base64 = base64.b64encode(archivo_optimizado.read()).decode('utf-8')
        
        # Parámetros para la API de imgbb
        payload = {
            'key': current_app.config['IMGBB_API_KEY'],
            'image': archivo_base64
        }
        
        # Hacer la petición
        response = requests.post(current_app.config['IMGBB_API_URL'], payload)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']['url'], "Imagen subida exitosamente"
        
        return None, f"Error del servidor de imágenes (código {response.status_code})"
        
    except Exception as e:
        print(f"Error al subir imagen: {e}")
        return None, f"Error al procesar la imagen: {str(e)}"

@productos_bp.route('/admin')
@login_required
def admin_dashboard():
    """Dashboard de administrador"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    total_productos = Producto.query.count()
    productos_sin_stock = Producto.query.filter(Producto.stock <= 0).count()
    categorias_count = Categoria.query.count()
    
    # Calcular pedidos de hoy usando la zona horaria de Perú
    from datetime import datetime, timedelta
    import pytz
    from app.models import Pedido
    
    # Zona horaria de Perú
    peru_tz = pytz.timezone('America/Lima')
    ahora = datetime.now(peru_tz)
    inicio_del_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_del_dia = inicio_del_dia + timedelta(days=1)
    
    # Contar pedidos del día actual
    pedidos_hoy = Pedido.query.filter(
        Pedido.fecha >= inicio_del_dia.astimezone(pytz.UTC),
        Pedido.fecha < fin_del_dia.astimezone(pytz.UTC)
    ).count()
    
    productos_recientes = Producto.query.limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_productos=total_productos,
                         productos_sin_stock=productos_sin_stock,
                         categorias_count=categorias_count,
                         pedidos_hoy=pedidos_hoy,
                         productos_recientes=productos_recientes)

@productos_bp.route('/admin/productos')
@login_required
def admin_listar_productos():
    """Lista productos para administradores"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    categoria_id = request.args.get('categoria', type=int)
    busqueda = request.args.get('q', '')
    
    query = Producto.query
    
    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)
    
    if busqueda:
        query = query.filter(Producto.nombre.contains(busqueda))
    
    productos = query.all()
    categorias = Categoria.query.all()
    
    return render_template('admin/productos_lista.html',
                         productos=productos,
                         categorias=categorias,
                         categoria_seleccionada=categoria_id,
                         busqueda=busqueda)

@productos_bp.route('/admin/producto/nuevo', methods=['GET', 'POST'])
@login_required
def admin_nuevo_producto():
    """Crear nuevo producto"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        id_categoria = request.form.get('id_categoria')
        imagen = request.files.get('imagen')
        
        # Validaciones
        if not all([nombre, precio, stock, id_categoria]):
            flash('Por favor complete todos los campos obligatorios', 'error')
            return render_template('admin/producto_form.html', 
                                 categorias=Categoria.query.all())
        
        try:
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            flash('Precio y stock deben ser números válidos', 'error')
            return render_template('admin/producto_form.html', 
                                 categorias=Categoria.query.all())
        
        # Subir imagen si se proporciona
        imagen_url = None
        if imagen and imagen.filename:
            imagen_url, mensaje = subir_imagen_imgbb(imagen)
            if imagen_url:
                flash(mensaje, 'success')
            else:
                flash(f'No se pudo subir la imagen: {mensaje} El producto se creará sin imagen.', 'error')
        
        # Crear producto
        nuevo_producto = Producto(
            nombre=nombre,
            precio=precio,
            stock=stock,
            id_categoria=int(id_categoria),
            imagen_url=imagen_url
        )
        
        try:
            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('productos.admin_listar_productos'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear el producto', 'error')
    
    categorias = Categoria.query.all()
    return render_template('admin/producto_form.html', categorias=categorias)

@productos_bp.route('/admin/producto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_producto(id):
    """Editar producto existente"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Validar y asignar campos obligatorios
            nombre = request.form.get('nombre')
            precio = request.form.get('precio')
            stock = request.form.get('stock')
            id_categoria = request.form.get('id_categoria')
            
            if not all([nombre, precio, stock, id_categoria]):
                flash('Todos los campos obligatorios deben ser completados', 'error')
                categorias = Categoria.query.all()
                return render_template('admin/producto_form.html', producto=producto, categorias=categorias)
            
            producto.nombre = nombre
            producto.precio = float(precio)
            producto.stock = int(stock)
            producto.id_categoria = int(id_categoria)
            
        
            # Manejar imagen nueva
            imagen = request.files.get('imagen')
            if imagen and imagen.filename:
                imagen_url, mensaje = subir_imagen_imgbb(imagen)
                if imagen_url:
                    producto.imagen_url = imagen_url
                    flash(f'Imagen actualizada: {mensaje}', 'success')
                else:
                    flash(f'No se pudo actualizar la imagen: {mensaje}', 'error')
        
            db.session.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('productos.admin_listar_productos'))
            
        except ValueError as e:
            flash('Error en los datos del formulario. Verifica que el precio y stock sean números válidos.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el producto', 'error')
    
    categorias = Categoria.query.all()
    return render_template('admin/producto_form.html', producto=producto, categorias=categorias)

@productos_bp.route('/admin/producto/<int:id>/eliminar', methods=['POST'])
@login_required
def admin_eliminar_producto(id):
    """Desactivar producto (soft delete)"""
    if not current_user.is_admin():
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    producto = Producto.query.get_or_404(id)
    
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el producto', 'error')
    
    return redirect(url_for('productos.admin_listar_productos'))

@productos_bp.route('/admin/categorias')
@login_required
def admin_listar_categorias():
    """Lista categorías para administradores"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    # Obtener parámetro de búsqueda
    buscar = request.args.get('buscar', '').strip()
    
    # Construir consulta base
    query = Categoria.query
    
    # Aplicar filtro de búsqueda si existe
    if buscar:
        query = query.filter(Categoria.nombre.ilike(f'%{buscar}%'))
    
    # Ordenar por ID descendente (más recientes primero)
    categorias = query.order_by(Categoria.id_categoria.desc()).all()
    
    return render_template('admin/categorias_lista.html', categorias=categorias)

@productos_bp.route('/admin/categoria/nueva', methods=['GET', 'POST'])
@login_required
def admin_nueva_categoria():
    """Crear nueva categoría"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        
        if not nombre:
            flash('El nombre de la categoría es obligatorio', 'error')
            return render_template('admin/categoria_form.html')
        
        nueva_categoria = Categoria(nombre=nombre)
        
        try:
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría creada exitosamente', 'success')
            return redirect(url_for('productos.admin_listar_categorias'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la categoría', 'error')
    
    return render_template('admin/categoria_form.html')

@productos_bp.route('/admin/categoria/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_categoria(id):
    """Editar categoría existente"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    categoria = Categoria.query.get_or_404(id)
    
    if request.method == 'POST':
        categoria.nombre = request.form.get('nombre')
        
        try:
            db.session.commit()
            flash('Categoría actualizada exitosamente', 'success')
            return redirect(url_for('productos.admin_listar_categorias'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la categoría', 'error')
    
    return render_template('admin/categoria_form.html', categoria=categoria)

@productos_bp.route('/admin/categoria/<int:id>/eliminar', methods=['POST'])
@login_required
def admin_eliminar_categoria(id):
    """Eliminar categoría"""
    if not current_user.is_admin():
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    categoria = Categoria.query.get_or_404(id)
    
    # Verificar si la categoría tiene productos
    if categoria.productos:
        flash(f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene {len(categoria.productos)} productos asociados', 'error')
        return redirect(url_for('productos.admin_listar_categorias'))
    
    try:
        nombre_categoria = categoria.nombre
        db.session.delete(categoria)
        db.session.commit()
        flash(f'Categoría "{nombre_categoria}" eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la categoría', 'error')
    
    return redirect(url_for('productos.admin_listar_categorias'))

@productos_bp.route('/api/validar-imagen', methods=['POST'])
@login_required
def api_validar_imagen():
    """
    API endpoint para validar imágenes via AJAX
    Retorna: JSON con resultado de validación
    """
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        imagen = request.files.get('imagen')
        if not imagen:
            return jsonify({'success': False, 'message': 'No se recibió ningún archivo'}), 400
        
        es_valido, mensaje = validar_archivo_imagen(imagen)
        
        response_data = {
            'success': es_valido,
            'message': mensaje,
            'filename': imagen.filename,
            'size': len(imagen.read()) if imagen else 0
        }
        
        # Resetear el archivo para uso posterior
        imagen.seek(0)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al validar imagen: {str(e)}'
        }), 500