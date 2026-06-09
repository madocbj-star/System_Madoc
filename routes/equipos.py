from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_required

from werkzeug.utils import secure_filename

import os

from extensions import db

from models.equipo import Equipo
from models.cliente import Cliente
from models.orden import Orden
from models.usuario import Usuario

from datetime import datetime
from sqlalchemy import func

from utils.permisos import rol_requerido

# =========================================
# CREAR BLUEPRINT
# =========================================

equipos = Blueprint(
    'equipos',
    __name__,
    url_prefix='/equipos'
)

# =========================================
# LISTAR EQUIPOS
# =========================================

@equipos.route('/')
@login_required
@rol_requerido('admin', 'tecnico')
def listar_equipos():

    lista_equipos = Equipo.query.order_by(
        Equipo.id.desc()
    ).all()

    return render_template(
        'equipos/index.html',
        equipos=lista_equipos
    )

# =========================================
# CREAR EQUIPO
# =========================================

@equipos.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'tecnico')
def crear_equipo():

    clientes = Cliente.query.order_by(
        Cliente.nombre.asc()
    ).all()

    tecnicos = Usuario.query.filter(
        Usuario.rol.in_(['admin', 'tecnico']),
        Usuario.estado == True
    ).order_by(Usuario.nombre.asc()).all()

    if request.method == 'POST':

        foto_nombre = None

        # =========================================
        # SUBIR FOTO
        # =========================================

        foto = request.files.get('foto')

        if foto and foto.filename != '':

            foto_nombre = secure_filename(foto.filename)

            ruta_guardado = os.path.join(
                'static/uploads/equipos',
                foto_nombre
            )

            foto.save(ruta_guardado)

        # =========================================
        # CREAR EQUIPO
        # =========================================

        nuevo_equipo = Equipo(

            tipo=request.form['tipo'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            serial=request.form['serial'],
            estado_fisico=request.form['estado_fisico'],
            accesorios=request.form['accesorios'],
            password_equipo=request.form['password_equipo'],
            observaciones=request.form['observaciones'],
            cliente_id=request.form['cliente_id'],
            foto=foto_nombre

        )

        db.session.add(nuevo_equipo)
        db.session.commit()

        # =========================================
        # CREAR ORDEN AUTOMÁTICA
        # =========================================

        max_id = db.session.query(func.max(Orden.id)).scalar() or 0
        codigo_orden = f'SER-JUL-{max_id + 1:04d}'

        tecnico_id = request.form.get('tecnico_id') or None

        nueva_orden = Orden(

            codigo_orden=codigo_orden,

            problema_reportado=request.form[
                'observaciones'
            ],

            diagnostico='',

            solucion='',

            estado='RECIBIDO',

            valor_servicio=0,

            observaciones='',

            equipo_id=nuevo_equipo.id,

            tecnico_id=tecnico_id

        )

        db.session.add(nueva_orden)
        db.session.commit()

        flash('Equipo registrado correctamente', 'success')

        return redirect(url_for('equipos.listar_equipos'))

    return render_template(
        'equipos/crear.html',
        clientes=clientes,
        tecnicos=tecnicos
    )

# =========================================
# VER EQUIPO
# =========================================

@equipos.route('/ver/<int:id>')
@login_required
@rol_requerido('admin', 'tecnico')
def ver_equipo(id):

    equipo = Equipo.query.get_or_404(id)

    return render_template(
        'equipos/ver.html',
        equipo=equipo
    )

# =========================================
# EDITAR EQUIPO
# =========================================

@equipos.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'tecnico')
def editar_equipo(id):

    equipo = Equipo.query.get_or_404(id)

    clientes = Cliente.query.order_by(
        Cliente.nombre.asc()
    ).all()

    if request.method == 'POST':

        equipo.tipo = request.form['tipo']
        equipo.marca = request.form['marca']
        equipo.modelo = request.form['modelo']
        equipo.serial = request.form['serial']

        equipo.estado_fisico = request.form['estado_fisico']
        equipo.accesorios = request.form['accesorios']
        equipo.password_equipo = request.form['password_equipo']
        equipo.observaciones = request.form['observaciones']
        equipo.cliente_id = request.form['cliente_id']

        db.session.commit()

        flash('Equipo actualizado correctamente', 'success')

        return redirect(url_for('equipos.listar_equipos'))

    return render_template(
        'equipos/editar.html',
        equipo=equipo,
        clientes=clientes
    )