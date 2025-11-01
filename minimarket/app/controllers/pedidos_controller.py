from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app.models import Pedido, PedidoDetalle, Producto, Usuario, Rol, db
from datetime import datetime, timedelta
from sqlalchemy import text


pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/carrito')
def ver_carrito():
    """Muestra el carrito de compras"""
    carrito = session.get('carrito', {})
    productos_carrito = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        if producto:
            subtotal = producto.precio * cantidad
            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('carrito/ver_carrito.html', 
                         productos_carrito=productos_carrito, 
                         total=total)

@pedidos_bp.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    """Valida stock usando SP simplificado"""
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if not producto_id:
        return jsonify({'success': False, 'message': 'Producto no válido'})
    
    try:
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            EXEC sp_obtener_producto_validar 
                @id_producto = ?,
                @cantidad_solicitada = ?
        """, (producto_id, cantidad))
        
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not result:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        # Desempacar resultado
        id_prod, nombre, precio, stock, existe, stock_suficiente = result
        
        if not existe:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        if not stock_suficiente:
            return jsonify({'success': False, 'message': 'Stock con sp insuficiente'})
        
        # Agregar al carrito
        if 'carrito' not in session:
            session['carrito'] = {}
        
        carrito = session['carrito']
        carrito[str(producto_id)] = carrito.get(str(producto_id), 0) + cantidad
        session['carrito'] = carrito
        session.modified = True
        
        return jsonify({
            'success': True, 
            'message': f'Producto "{nombre}" con sp agregado al carrito',
            'total_items': sum(carrito.values())
        })
        
    except Exception as e:
        print(f"Error detallado: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@pedidos_bp.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    """Actualiza la cantidad de un producto en el carrito"""
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 0))
    
    if 'carrito' not in session:
        session['carrito'] = {}
    
    carrito = session['carrito']
    
    if cantidad <= 0:
        # Eliminar del carrito
        if producto_id in carrito:
            del carrito[producto_id]
    else:
        # Verificar stock
        producto = Producto.query.get(int(producto_id))
        if producto and cantidad <= producto.stock:
            carrito[producto_id] = cantidad
        else:
            flash('Stock insuficiente', 'error')
            return redirect(url_for('pedidos.ver_carrito'))
    
    session['carrito'] = carrito
    session.modified = True
    
    return redirect(url_for('pedidos.ver_carrito'))

@pedidos_bp.route('/eliminar_carrito/<int:producto_id>')
def eliminar_carrito(producto_id):
    """Elimina un producto del carrito"""
    if 'carrito' in session:
        carrito = session['carrito']
        if str(producto_id) in carrito:
            del carrito[str(producto_id)]
            session['carrito'] = carrito
            session.modified = True
            flash('Producto eliminado del carrito', 'info')
    
    return redirect(url_for('pedidos.ver_carrito'))

@pedidos_bp.route('/checkout')
@login_required
def checkout():
    """Página de checkout"""
    carrito = session.get('carrito', {})
    
    if not carrito:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('main.index'))
    
    productos_carrito = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        if producto:
            if cantidad > producto.stock:
                flash(f'Stock insuficiente para {producto.nombre}', 'error')
                return redirect(url_for('pedidos.ver_carrito'))
            
            subtotal = producto.precio * cantidad
            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('carrito/checkout.html', 
                         productos_carrito=productos_carrito, 
                         total=total,
                         usuario=current_user)

@pedidos_bp.route('/procesar_pedido', methods=['POST'])
@login_required
def procesar_pedido():
    """Procesa un pedido y lo guarda en la base de datos"""
    carrito = session.get('carrito', {})
    
    if not carrito:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('main.index'))
    
    es_delivery = request.form.get('es_delivery') == 'on'
    
    # Validaciones
    if es_delivery and not current_user.direccion:
        flash('Debes tener una dirección registrada en tu perfil para solicitar delivery', 'error')
        return redirect(url_for('auth.editar_perfil'))
    
    if not current_user.telefono:
        flash('Debes tener un teléfono registrado en tu perfil para realizar pedidos', 'error')
        return redirect(url_for('auth.editar_perfil'))
    
    try:
        # Crear el pedido
        nuevo_pedido = Pedido(
            id_usuario=current_user.id_usuario,
            total=0,  # Se calculará después
            es_delivery=es_delivery
        )
        
        db.session.add(nuevo_pedido)
        db.session.flush()  # Para obtener el ID del pedido
        
        total_pedido = 0
        
        # Agregar detalles del pedido
        for producto_id, cantidad in carrito.items():
            producto = Producto.query.get(int(producto_id))
            
            if not producto:
                raise Exception(f'Producto {producto_id} no válido')
            
            if cantidad > producto.stock:
                raise Exception(f'Stock insuficiente para {producto.nombre}')
            
            # Crear detalle del pedido
            detalle = PedidoDetalle(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            
            db.session.add(detalle)
            
            # Actualizar stock
            producto.stock -= cantidad
            
            total_pedido += cantidad * producto.precio
        
        # Actualizar total del pedido
        nuevo_pedido.total = total_pedido
        
        db.session.commit()
        
        # Limpiar carrito
        session['carrito'] = {}
        session.modified = True
        
        flash('¡Pedido realizado exitosamente!', 'success')
        return redirect(url_for('pedidos.detalle_pedido', id=nuevo_pedido.id_pedido))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el pedido: {str(e)}', 'error')
        return redirect(url_for('pedidos.checkout'))

@pedidos_bp.route('/mis_pedidos')
@login_required
def mis_pedidos():
    """Lista los pedidos del usuario actual"""
    pedidos = Pedido.query.filter_by(id_usuario=current_user.id_usuario)\
                          .order_by(Pedido.id_pedido.desc()).all()
    
    return render_template('pedidos/mis_pedidos.html', pedidos=pedidos)

@pedidos_bp.route('/pedido/<int:id>')
@login_required
def detalle_pedido(id):
    """Muestra el detalle de un pedido específico"""
    pedido = Pedido.query.get_or_404(id)
    
    # Verificar que el usuario tenga permisos para ver este pedido
    tiene_permisos = (
        current_user.is_admin() or  # Admin puede ver todos
        pedido.id_usuario == current_user.id_usuario or  # Cliente puede ver sus pedidos
        (current_user.is_repartidor() and pedido.repartidor_id == current_user.id_usuario)  # Repartidor puede ver pedidos asignados
    )
    
    if not tiene_permisos:
        flash('No tienes permisos para ver este pedido', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('pedidos/detalle_pedido.html', pedido=pedido)

@pedidos_bp.route('/admin/pedidos')
@login_required
def admin_listar_pedidos():
    """Lista todos los pedidos para administradores"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    estado = request.args.get('estado')
    busqueda = request.args.get('q')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    query = Pedido.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    if busqueda:
        # Especificar explícitamente que queremos hacer JOIN con el usuario del pedido (cliente)
        query = query.join(Usuario, Pedido.id_usuario == Usuario.id_usuario).filter(Usuario.nombre_completo.contains(busqueda))
    
    # Filtros de fecha
    if fecha_desde:
        try:
            fecha_inicio = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Pedido.fecha >= fecha_inicio)
        except ValueError:
            pass  # Ignorar fechas inválidas
    
    if fecha_hasta:
        try:
            fecha_fin = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Agregar 1 día para incluir todo el día hasta
            fecha_fin = fecha_fin + timedelta(days=1)
            query = query.filter(Pedido.fecha < fecha_fin)
        except ValueError:
            pass  # Ignorar fechas inválidas
    
    pedidos = query.order_by(Pedido.id_pedido.desc()).all()
    
    # Obtener lista de repartidores disponibles (usuarios con rol repartidor)
    repartidores = Usuario.query.join(Rol).filter(Rol.nombre.ilike('%repartidor%')).all()
    
    # Calcular estadísticas
    todos_pedidos = Pedido.query.all()
    stats = {
        'total': len(todos_pedidos),
        'pendientes': len([p for p in todos_pedidos if p.estado == 'pendiente']),
        'confirmados': len([p for p in todos_pedidos if p.estado == 'confirmado']),
        'en_preparacion': len([p for p in todos_pedidos if p.estado == 'en_preparacion']),
        'en_camino': len([p for p in todos_pedidos if p.estado == 'en_camino']),
        'entregados': len([p for p in todos_pedidos if p.estado == 'entregado']),
        'cancelados': len([p for p in todos_pedidos if p.estado == 'cancelado'])
    }
    
    return render_template('admin/pedidos_lista.html', 
                         pedidos=pedidos, 
                         estado_filtro=estado,
                         fecha_desde_filtro=fecha_desde,
                         fecha_hasta_filtro=fecha_hasta,
                         busqueda_filtro=busqueda,
                         stats=stats,
                         repartidores=repartidores)

@pedidos_bp.route('/repartidor/pedidos')
@login_required
def repartidor_mis_pedidos():
    """Lista los pedidos asignados al repartidor"""
    if not current_user.is_repartidor():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    # Obtener solo los pedidos asignados a este repartidor
    pedidos_asignados = Pedido.query.filter_by(repartidor_id=current_user.id_usuario).order_by(Pedido.id_pedido.desc()).all()
    
    # Calcular estadísticas del repartidor
    stats = {
        'total': len(pedidos_asignados),
        'en_camino': len([p for p in pedidos_asignados if p.estado == 'en_camino']),
        'entregados': len([p for p in pedidos_asignados if p.estado == 'entregado']),
        'cancelados': len([p for p in pedidos_asignados if p.estado == 'cancelado'])
    }
    
    return render_template('repartidor/pedidos_lista.html', 
                         pedidos=pedidos_asignados, 
                         stats=stats)

@pedidos_bp.route('/admin/pedido/<int:id>')
@login_required
def admin_ver_pedido(id):
    """Ver detalles de un pedido específico para administradores"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    pedido = Pedido.query.get_or_404(id)
    return render_template('admin/pedido_detalle.html', pedido=pedido)

@pedidos_bp.route('/admin/pedido/<int:id>/imprimir')
@login_required
def admin_imprimir_pedido(id):
    """Generar versión imprimible de un pedido para administradores"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    pedido = Pedido.query.get_or_404(id)
    from datetime import datetime
    current_time = datetime.now()
    return render_template('admin/pedido_imprimir.html', pedido=pedido, current_time=current_time)

@pedidos_bp.route('/admin/pedido/<int:id>/estado', methods=['POST'])
@login_required
def admin_cambiar_estado(id):
    """Cambia estado usando SP"""
    if not current_user.is_admin():
        flash('No tienes permisos', 'error')
        return redirect(url_for('main.index'))
    
    nuevo_estado = request.form.get('estado')
    repartidor_id = request.form.get('repartidor_id') or None
    
    estados_validos = ['pendiente', 'confirmado', 'en_preparacion', 'en_camino', 'entregado', 'cancelado']
    
    if nuevo_estado not in estados_validos:
        flash('Estado no válido', 'error')
        return redirect(url_for('pedidos.admin_listar_pedidos'))
    
    try:
        query = text("""
            EXEC sp_actualizar_estado_pedido 
                @id_pedido = :id_pedido,
                @nuevo_estado = :estado,
                @repartidor_id = :repartidor_id
        """)
        
        db.session.execute(query, {
            'id_pedido': id,
            'estado': nuevo_estado,
            'repartidor_id': repartidor_id
        })
        db.session.commit()
        
        flash(f'Pedido #{id} actualizado con sp a {nuevo_estado}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('pedidos.admin_listar_pedidos'))


@pedidos_bp.route('/repartidor/pedidos/<int:id>/entregar', methods=['POST'])
@login_required
def repartidor_entregar_pedido(id):
    """Permite al repartidor marcar un pedido como entregado"""
    if not current_user.is_repartidor():
        if request.is_json:
            return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    pedido = Pedido.query.get_or_404(id)
    
    # Verificar que el pedido está asignado a este repartidor
    if pedido.repartidor_id != current_user.id_usuario:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Este pedido no está asignado a ti'})
        flash('Este pedido no está asignado a ti', 'error')
        return redirect(url_for('pedidos.repartidor_mis_pedidos'))
    
    # Solo puede cambiar de "en_camino" a "entregado"
    if pedido.estado != 'en_camino':
        if request.is_json:
            return jsonify({'success': False, 'message': 'Solo puedes entregar pedidos que están en camino'})
        flash('Solo puedes entregar pedidos que están en camino', 'error')
        return redirect(url_for('pedidos.repartidor_mis_pedidos'))
    
    pedido.estado = 'entregado'
    
    try:
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': f'Pedido #{pedido.id_pedido} marcado como entregado exitosamente'})
        
        flash(f'Pedido #{pedido.id_pedido} marcado como entregado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        
        if request.is_json:
            return jsonify({'success': False, 'message': f'Error al entregar pedido: {str(e)}'})
        
        flash(f'Error al entregar pedido: {str(e)}', 'error')
    
    return redirect(url_for('pedidos.repartidor_mis_pedidos'))

@pedidos_bp.route('/pedidos/<int:id>/cancelar', methods=['GET', 'POST'])
@login_required
def cancelar_pedido(id):
    """Permite cancelar un pedido según permisos"""
    pedido = Pedido.query.get_or_404(id)
    
    # Si es GET, mostrar página de confirmación
    if request.method == 'GET':
        # Verificar permisos básicos para mostrar la página
        puede_ver = False
        if current_user.is_admin():
            puede_ver = True
        elif pedido.id_usuario == current_user.id_usuario:
            puede_ver = pedido.estado in ['pendiente', 'confirmado']
        elif current_user.is_repartidor() and pedido.repartidor_id == current_user.id_usuario:
            puede_ver = pedido.estado in ['en_preparacion', 'en_camino']
        
        if not puede_ver:
            flash('No tienes permisos para cancelar este pedido', 'error')
            return redirect(url_for('pedidos.mis_pedidos'))
            
        return render_template('pedidos/confirmar_cancelacion.html', pedido=pedido)
    
    # Si es POST, procesar la cancelación
    motivo_cancelacion = request.form.get('motivo') if not request.is_json else request.json.get('motivo', '')
    
    # Verificar permisos para cancelar
    puede_cancelar = False
    mensaje_error = ''
    
    if current_user.is_admin():
        # Admin puede cancelar cualquier pedido que no esté entregado
        puede_cancelar = pedido.estado != 'entregado'
        mensaje_error = 'No se pueden cancelar pedidos ya entregados'
        
    elif pedido.id_usuario == current_user.id_usuario:
        # Cliente puede cancelar sus pedidos solo si están pendientes o confirmados
        puede_cancelar = pedido.estado in ['pendiente', 'confirmado']
        mensaje_error = 'Solo puedes cancelar pedidos pendientes o confirmados'
        
    elif current_user.is_repartidor() and pedido.repartidor_id == current_user.id_usuario:
        # Repartidor puede cancelar solo si hay un problema y no está entregado
        puede_cancelar = pedido.estado in ['en_preparacion', 'en_camino'] and motivo_cancelacion
        mensaje_error = 'Solo puedes cancelar pedidos en preparación o en camino, y debes proporcionar un motivo'
    else:
        mensaje_error = 'No tienes permisos para cancelar este pedido'
    
    if not puede_cancelar:
        if request.is_json:
            return jsonify({'success': False, 'message': mensaje_error})
        flash(mensaje_error, 'error')
        return redirect(request.referrer or url_for('main.index'))
    
    # Restaurar stock de productos si el pedido no estaba cancelado
    if pedido.estado != 'cancelado':
        try:
            for detalle in pedido.detalles:
                producto = detalle.producto
                producto.stock += detalle.cantidad
            
            # Cambiar estado a cancelado
            pedido.estado = 'cancelado'
            
            # Opcional: guardar motivo de cancelación (requeriría nueva columna en BD)
            # pedido.motivo_cancelacion = motivo_cancelacion
            
            db.session.commit()
            
            # Mensaje de confirmación
            mensaje_exito = f'Pedido #{pedido.id_pedido} cancelado exitosamente'
            if motivo_cancelacion:
                mensaje_exito += f'. Motivo: {motivo_cancelacion}'
            
            if request.is_json:
                return jsonify({'success': True, 'message': mensaje_exito})
            
            flash(mensaje_exito, 'success')
            
        except Exception as e:
            db.session.rollback()
            error_msg = f'Error al cancelar pedido: {str(e)}'
            
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg})
            
            flash(error_msg, 'error')
    else:
        mensaje = f'El pedido #{pedido.id_pedido} ya estaba cancelado'
        if request.is_json:
            return jsonify({'success': False, 'message': mensaje})
        flash(mensaje, 'info')
    
    # Redirigir según el rol del usuario
    if current_user.is_admin():
        return redirect(url_for('pedidos.admin_listar_pedidos'))
    elif current_user.is_repartidor():
        return redirect(url_for('pedidos.repartidor_mis_pedidos'))
    else:
        return redirect(url_for('pedidos.mis_pedidos'))
