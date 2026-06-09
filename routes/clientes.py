from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_required

from utils.permisos import rol_requerido

from models.cliente import Cliente
from extensions import db

# =========================================
# CREAR BLUEPRINT
# =========================================

clientes = Blueprint(
    'clientes',
    __name__,
    url_prefix='/clientes'
)

# =========================================
# LISTAR CLIENTES
# =========================================

@clientes.route('/')
@login_required
@rol_requerido('admin', 'vendedor')
def listar_clientes():

    lista_clientes = Cliente.query.order_by(
        Cliente.id.desc()
    ).all()

    return render_template(
        'clientes/index.html',
        clientes=lista_clientes
    )

# =========================================
# CREAR CLIENTE
# =========================================

@clientes.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'vendedor')
def crear_cliente():

    if request.method == 'POST':

        nuevo_cliente = Cliente(

            nombre=request.form['nombre'],
            documento=request.form['documento'],
            telefono=request.form['telefono'],
            correo=request.form['correo'],
            direccion=request.form['direccion'],
            empresa=request.form['empresa'],
            observaciones=request.form['observaciones']

        )

        db.session.add(nuevo_cliente)
        db.session.commit()

        flash(
            'Cliente registrado correctamente',
            'success'
        )

        return redirect(
            url_for('clientes.listar_clientes')
        )

    return render_template(
        'clientes/crear.html'
    )

# =========================================
# EDITAR CLIENTE
# =========================================

@clientes.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'vendedor')
def editar_cliente(id):

    cliente = Cliente.query.get_or_404(id)

    if request.method == 'POST':

        cliente.nombre = request.form['nombre']
        cliente.documento = request.form['documento']
        cliente.telefono = request.form['telefono']
        cliente.correo = request.form['correo']
        cliente.direccion = request.form['direccion']
        cliente.empresa = request.form['empresa']
        cliente.observaciones = request.form['observaciones']

        db.session.commit()

        flash(
            'Cliente actualizado correctamente',
            'success'
        )

        return redirect(
            url_for('clientes.listar_clientes')
        )

    return render_template(
        'clientes/editar.html',
        cliente=cliente
    )

# =========================================
# ELIMINAR CLIENTE
# =========================================

@clientes.route('/eliminar/<int:id>')
@login_required
@rol_requerido('admin', 'vendedor')
def eliminar_cliente(id):

    cliente = Cliente.query.get_or_404(id)

    db.session.delete(cliente)
    db.session.commit()

    flash(
        'Cliente eliminado correctamente',
        'info'
    )

    return redirect(
        url_for('clientes.listar_clientes')
    )