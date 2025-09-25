from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario, Rol, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el login de usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor complete todos los campos', 'error')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password):
            login_user(usuario, remember=True)
            flash(f'¡Bienvenido {usuario.nombre_completo}!', 'success')
            
            # Redirigir según el rol
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif usuario.is_admin():
                return redirect(url_for('productos.admin_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de nuevos usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        
        # Validaciones
        if not all([nombre_completo, email, password, confirm_password]):
            flash('Por favor complete todos los campos obligatorios', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('auth/register.html')
        
        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('El email ya está registrado', 'error')
            return render_template('auth/register.html')
        
        # Crear nuevo usuario (por defecto con rol cliente)
        rol_cliente = Rol.query.filter_by(nombre='cliente').first()
        if not rol_cliente:
            flash('Error del sistema: rol cliente no encontrado', 'error')
            return render_template('auth/register.html')
        
        nuevo_usuario = Usuario(
            nombre_completo=nombre_completo,
            email=email,
            telefono=telefono,
            direccion=direccion,
            id_rol=rol_cliente.id_rol
        )
        nuevo_usuario.set_password(password)
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Registro exitoso. ¡Ya puedes iniciar sesión!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la cuenta. Intenta nuevamente.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/perfil')
@login_required
def perfil():
    """Muestra el perfil del usuario actual"""
    return render_template('auth/perfil.html', usuario=current_user)

@auth_bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Permite editar el perfil del usuario"""
    if request.method == 'POST':
        current_user.nombre_completo = request.form.get('nombre_completo')
        current_user.telefono = request.form.get('telefono')
        current_user.direccion = request.form.get('direccion')
        
        # Cambiar contraseña si se proporciona
        new_password = request.form.get('new_password')
        if new_password:
            if len(new_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('auth/editar_perfil.html')
            current_user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('auth.perfil'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil', 'error')
    
    return render_template('auth/editar_perfil.html')