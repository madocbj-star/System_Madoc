### Pendiente recortar los from flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from models.cliente import Cliente
from models.equipo import Equipo
from models.orden import Orden
from models.producto import Producto
from models.detalle_venta import DetalleVenta

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from models.usuario import Usuario

from extensions import db

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from extensions import mail
from flask import current_app

# =========================================
# CREAR BLUEPRINT
# =========================================

auth = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)

# =========================================
# SERIALIZER TOKEN
# =========================================

def get_serializer():
    return URLSafeTimedSerializer(
        current_app.config['SECRET_KEY']
    )

# =========================================
# LOGIN
# =========================================

@auth.route('/login', methods=['GET', 'POST'])
def login():

    # SI YA INICIÓ SESIÓN
    if current_user.is_authenticated:

        return redirect(url_for('auth.dashboard'))

    # SI ENVÍA FORMULARIO
    if request.method == 'POST':

        correo = request.form.get('correo')
        password = request.form.get('password')
        remember = request.form.get('remember')

        # BUSCAR USUARIO
        usuario = Usuario.query.filter_by(
            correo=correo
        ).first()

        # VALIDAR USUARIO
        if usuario and check_password_hash(
            usuario.password,
            password
        ):

            login_user(
                usuario,
                remember=remember
            )

            flash(
                'Bienvenido al sistema',
                'success'
            )

            return redirect(
                url_for('auth.dashboard')
            )

        else:

            flash(
                'Correo o contraseña incorrectos',
                'danger'
            )

    return render_template('auth/login.html')

# =========================================
# DASHBOARD
# =========================================

@auth.route('/dashboard')
@login_required
def dashboard():

    total_clientes = Cliente.query.count()

    total_equipos = Equipo.query.count()

    total_ordenes = Orden.query.count()

    total_productos = Producto.query.count()

    ordenes_pendientes = Orden.query.filter(
        Orden.estado != 'ENTREGADO'
    ).count()

    stock_bajo = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo
    ).count()

    ultimas_ordenes = Orden.query.order_by(
        Orden.id.desc()
    ).limit(5).all()

    productos_stock_bajo = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo
    ).all()

    return render_template(

        'dashboard/index.html',

        total_clientes=total_clientes,

        total_equipos=total_equipos,

        total_ordenes=total_ordenes,

        total_productos=total_productos,

        ordenes_pendientes=ordenes_pendientes,

        stock_bajo=stock_bajo,

        ultimas_ordenes=ultimas_ordenes,

        productos_stock_bajo=productos_stock_bajo

    )

# =========================================
# LOGOUT
# =========================================

@auth.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        'Sesión cerrada correctamente',
        'info'
    )

    return redirect(
        url_for('auth.login')
    )

# =========================================
# RECUPERAR PASSWORD
# =========================================

@auth.route('/recuperar-password',
            methods=['GET', 'POST'])
def recuperar_password():

    if request.method == 'POST':

        correo = request.form.get('correo')

        usuario = Usuario.query.filter_by(
            correo=correo
        ).first()

        if usuario:

            # GENERAR TOKEN

            token = get_serializer().dumps(
                usuario.correo,
                salt='recuperar-password'
            )

            # LINK RECUPERACION

            enlace = url_for(
                'auth.reset_password',
                token=token,
                _external=True
            )

            # CREAR MENSAJE

            mensaje = Message(

                'Recuperación Contraseña - System Madoc',

                recipients=[usuario.correo]

            )

            mensaje.body = f'''

        Hola {usuario.nombre},

        Haz clic en el siguiente enlace para cambiar tu contraseña:

        {enlace}

        Si no solicitaste este cambio, ignora este mensaje.

        System Madoc
        '''

            # ENVIAR EMAIL

            mail.send(mensaje)

            flash(
                'Correo enviado correctamente',
                'success'
            )

        else:

            flash(
                'Correo no encontrado',
                'danger'
            )

    return render_template(
        'auth/recuperar_password.html'
    )

# =========================================
# PERFIL USUARIO
# =========================================

@auth.route('/perfil',
            methods=['GET', 'POST'])
@login_required
def perfil():

    usuario = current_user

    if request.method == 'POST':

        usuario.nombre = request.form['nombre']

        usuario.correo = request.form['correo']

        # FOTO

        foto = request.files.get('foto')

        if foto and foto.filename != '':

            from utils.cloudinary_helper import subir_imagen

            url_foto = subir_imagen(foto, 'usuarios')

            if url_foto:
                usuario.foto = url_foto

        # PASSWORD

        nueva_password = request.form.get(
            'password'
        )

        if nueva_password != '':

            usuario.password = generate_password_hash(
                nueva_password
            )

        db.session.commit()

        flash(
            'Perfil actualizado correctamente',
            'success'
        )

        return redirect('/auth/perfil')

    return render_template(
        'auth/perfil.html',
        usuario=usuario
    )

# =========================================
# RESET PASSWORD
# =========================================

@auth.route('/reset-password/<token>',
            methods=['GET', 'POST'])
def reset_password(token):

    try:

        correo = get_serializer().loads(
            token,
            salt='recuperar-password',
            max_age=3600
        )

    except:

        flash(
            'El enlace es inválido o expiró',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )

    usuario = Usuario.query.filter_by(
        correo=correo
    ).first()

    if not usuario:

        flash(
            'Usuario no encontrado',
            'danger'
        )

        return redirect(
            url_for('auth.login')
        )

    if request.method == 'POST':

        nueva_password = request.form.get(
            'password'
        )

        usuario.password = generate_password_hash(
            nueva_password
        )

        db.session.commit()

        flash(
            'Contraseña actualizada correctamente',
            'success'
        )

        return redirect(
            url_for('auth.login')
        )

    return render_template(
        'auth/reset_password.html'
    )