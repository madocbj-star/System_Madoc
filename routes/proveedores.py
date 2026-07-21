from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required
from utils.permisos import rol_requerido
from extensions import db
from models.proveedor import Proveedor

proveedores = Blueprint(
    'proveedores',
    __name__,
    url_prefix='/proveedores'
)


# =========================================
# LISTAR PROVEEDORES
# =========================================

@proveedores.route('/')
@login_required
@rol_requerido('admin', 'almacen')
def listar_proveedores():

    lista = Proveedor.query.filter_by(
        activo=True
    ).order_by(Proveedor.nombre.asc()).all()

    return render_template(
        'proveedores/index.html',
        proveedores=lista
    )


# =========================================
# CREAR PROVEEDOR
# =========================================

@proveedores.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'almacen')
def crear_proveedor():

    if request.method == 'POST':

        nuevo = Proveedor(
            nombre=request.form['nombre'],
            nit_documento=request.form.get('nit_documento'),
            telefono=request.form.get('telefono'),
            correo=request.form.get('correo'),
            direccion=request.form.get('direccion'),
            activo=True
        )

        db.session.add(nuevo)
        db.session.commit()

        flash('Proveedor creado correctamente', 'success')

        return redirect(url_for('proveedores.listar_proveedores'))

    return render_template('proveedores/crear.html')


# =========================================
# EDITAR PROVEEDOR
# =========================================

@proveedores.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'almacen')
def editar_proveedor(id):

    proveedor = Proveedor.query.get_or_404(id)

    if request.method == 'POST':

        proveedor.nombre = request.form['nombre']
        proveedor.nit_documento = request.form.get('nit_documento')
        proveedor.telefono = request.form.get('telefono')
        proveedor.correo = request.form.get('correo')
        proveedor.direccion = request.form.get('direccion')

        db.session.commit()

        flash('Proveedor actualizado correctamente', 'success')

        return redirect(url_for('proveedores.listar_proveedores'))

    return render_template(
        'proveedores/editar.html',
        proveedor=proveedor
    )


# =========================================
# DESACTIVAR PROVEEDOR
# =========================================

@proveedores.route('/eliminar/<int:id>')
@login_required
@rol_requerido('admin', 'almacen')
def eliminar_proveedor(id):

    proveedor = Proveedor.query.get_or_404(id)

    proveedor.activo = False
    db.session.commit()

    flash('Proveedor archivado correctamente', 'success')

    return redirect(url_for('proveedores.listar_proveedores'))
