from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Usuario, Rol, db

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/admin/usuarios')
@login_required
def admin_listar_usuarios():
    """Lista usuarios para administradores"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    rol_id = request.args.get('rol', type=int)
    busqueda = request.args.get('q', '')
    
    query = Usuario.query
    
    if rol_id:
        query = query.filter_by(id_rol=rol_id)
    
    if busqueda:
        query = query.filter(Usuario.nombre_completo.contains(busqueda) | 
                           Usuario.email.contains(busqueda))
    
    usuarios = query.order_by(Usuario.id_usuario.desc()).all()
    roles = Rol.query.all()
    
    return render_template('admin/usuarios_lista.html', 
                         usuarios=usuarios, 
                         roles=roles,
                         rol_seleccionado=rol_id,
                         busqueda=busqueda)

@usuarios_bp.route('/admin/usuario/<int:id>')
@login_required
def admin_detalle_usuario(id):
    """Muestra el detalle de un usuario"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    return render_template('admin/usuario_detalle.html', usuario=usuario)

@usuarios_bp.route('/admin/usuario/<int:id>/estado', methods=['POST'])
@login_required
def admin_cambiar_estado_usuario(id):
    """Función deprecada - el campo activo no existe"""
    flash('Función no disponible', 'warning')
    return redirect(url_for('usuarios.admin_listar_usuarios'))

@usuarios_bp.route('/admin/usuario/<int:id>/rol', methods=['POST'])
@login_required
def admin_cambiar_rol_usuario(id):
    """Cambia el rol de un usuario"""
    if not current_user.is_admin():
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    nuevo_rol_id = request.form.get('id_rol')
    
    # No permitir cambiar el rol del mismo admin si es el único admin
    if (usuario.id_usuario == current_user.id_usuario and 
        usuario.is_admin() and 
        Usuario.query.join(Rol).filter(Rol.nombre == 'admin').count() == 1):
        flash('No puedes cambiar tu rol si eres el único administrador', 'error')
        return redirect(url_for('usuarios.admin_listar_usuarios'))
    
    if nuevo_rol_id:
        rol = Rol.query.get(int(nuevo_rol_id))
        if rol:
            usuario.id_rol = rol.id_rol
            
            try:
                db.session.commit()
                flash(f'Rol de usuario cambiado a {rol.nombre}', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error al cambiar el rol del usuario', 'error')
        else:
            flash('Rol no válido', 'error')
    
    return redirect(url_for('usuarios.admin_listar_usuarios'))

@usuarios_bp.route('/admin/usuario/nuevo', methods=['GET', 'POST'])
@login_required
def admin_nuevo_usuario():
    """Crear nuevo usuario"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            nuevo_usuario = Usuario()
            nuevo_usuario.nombre_completo = request.form.get('nombre_completo')
            nuevo_usuario.email = request.form.get('email')
            nuevo_usuario.telefono = request.form.get('telefono')
            nuevo_usuario.direccion = request.form.get('direccion')
            nuevo_usuario.id_rol = int(request.form.get('id_rol'))
            
            # Establecer contraseña
            password = request.form.get('password')
            nuevo_usuario.set_password(password)
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios.admin_listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al crear el usuario', 'error')
    
    roles = Rol.query.all()
    return render_template('admin/usuario_form.html', usuario=None, roles=roles)

@usuarios_bp.route('/admin/usuario/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_usuario(id):
    """Editar usuario existente"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            usuario.nombre_completo = request.form.get('nombre_completo')
            usuario.email = request.form.get('email')
            usuario.telefono = request.form.get('telefono')
            usuario.direccion = request.form.get('direccion')
            usuario.id_rol = int(request.form.get('id_rol'))
            
            # Solo actualizar contraseña si se proporciona una nueva
            new_password = request.form.get('password')
            if new_password:
                usuario.set_password(new_password)
            
            db.session.commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.admin_listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el usuario', 'error')
    
    roles = Rol.query.all()
    return render_template('admin/usuario_form.html', usuario=usuario, roles=roles)

@usuarios_bp.route('/admin/usuario/<int:id>/ver')
@login_required
def admin_ver_usuario(id):
    """Ver detalles del usuario"""
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    return render_template('admin/usuario_detalle.html', usuario=usuario)

@usuarios_bp.route('/admin/usuario/<int:id>/eliminar', methods=['POST'])
@login_required
def admin_eliminar_usuario(id):
    """Eliminar usuario"""
    if not current_user.is_admin():
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get_or_404(id)
    
    # No permitir eliminar al usuario actual
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes eliminarte a ti mismo', 'error')
        return redirect(url_for('usuarios.admin_listar_usuarios'))
    
    # No permitir eliminar al último administrador
    if usuario.rol.nombre == 'administrador':
        admin_count = Usuario.query.join(Rol).filter(Rol.nombre == 'administrador').count()
        if admin_count <= 1:
            flash('No puedes eliminar al último administrador del sistema', 'error')
            return redirect(url_for('usuarios.admin_listar_usuarios'))
    
    try:
        nombre_usuario = usuario.nombre_completo
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario "{nombre_usuario}" eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el usuario. Puede que tenga pedidos asociados.', 'error')
    
    return redirect(url_for('usuarios.admin_listar_usuarios'))