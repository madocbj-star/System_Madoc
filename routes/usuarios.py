from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import flash

from flask_login import login_required

from models.usuario import Usuario

from extensions import db

from utils.permisos import rol_requerido

from werkzeug.security import generate_password_hash

# =========================================
# BLUEPRINT
# =========================================

usuarios = Blueprint(
    'usuarios',
    __name__,
    url_prefix='/usuarios'
)

# =========================================
# LISTAR USUARIOS
# =========================================

@usuarios.route('/')
@login_required
@rol_requerido('admin')
def index():

    usuarios_db = Usuario.query.order_by(
        Usuario.id.desc()
    ).all()

    return render_template(
        'usuarios/index.html',
        usuarios=usuarios_db
    )

# =========================================
# CREAR USUARIO
# =========================================

@usuarios.route('/crear',
                methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def crear():

    if request.method == 'POST':

        nuevo_usuario = Usuario(

            nombre=request.form['nombre'],

            correo=request.form['correo'],

            password=generate_password_hash(
                request.form['password']
            ),

            rol=request.form['rol']

        )

        db.session.add(nuevo_usuario)

        db.session.commit()

        flash(
            'Usuario creado correctamente',
            'success'
        )

        return redirect('/usuarios')

    return render_template(
        'usuarios/crear.html'
    )

# =========================================
# VER USUARIO
# =========================================

@usuarios.route('/ver/<int:id>')
@login_required
@rol_requerido('admin')
def ver(id):

    usuario = Usuario.query.get_or_404(id)

    return render_template(
        'usuarios/ver.html',
        usuario=usuario
    )

# =========================================
# EDITAR USUARIO
# =========================================

@usuarios.route('/editar/<int:id>',
                methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def editar(id):

    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':

        usuario.nombre = request.form['nombre']

        usuario.correo = request.form['correo']

        usuario.rol = request.form['rol']

        usuario.estado = bool(
            request.form.get('estado') == '1'
        )

        db.session.commit()

        flash(
            'Usuario actualizado correctamente',
            'success'
        )

        return redirect('/usuarios')

    return render_template(
        'usuarios/editar.html',
        usuario=usuario
    )