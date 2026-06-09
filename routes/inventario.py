from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import login_required

from werkzeug.utils import secure_filename

import os

from extensions import db

from models.producto import Producto
from models.categoria_producto import CategoriaProducto

from utils.permisos import rol_requerido

# =========================================
# CREAR BLUEPRINT
# =========================================

inventario = Blueprint(
    'inventario',
    __name__,
    url_prefix='/inventario'
)

# =========================================
# LISTAR PRODUCTOS
# =========================================

@inventario.route('/')
@login_required
@rol_requerido('admin', 'almacen')
def listar_productos():

    productos = Producto.query.filter_by(
        activo=True
    ).order_by(
        Producto.id.desc()
    ).all()

    return render_template(
        'inventario/index.html',
        productos=productos
    )

# =========================================
# CREAR PRODUCTO
# =========================================

@inventario.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'almacen')
def crear_producto():

    categorias = CategoriaProducto.query.filter_by(
        activo=True
    ).order_by(
        CategoriaProducto.nombre.asc()
    ).all()

    if request.method == 'POST':

        foto_nombre = None

        # =========================================
        # SUBIR FOTO
        # =========================================

        foto = request.files.get('foto')

        if foto and foto.filename != '':

            foto_nombre = secure_filename(
                foto.filename
            )

            ruta_guardado = os.path.join(
                'static/uploads/productos',
                foto_nombre
            )

            foto.save(ruta_guardado)

        # =========================================
        # GENERAR CODIGO AUTOMATICO
        # =========================================

        categoria = CategoriaProducto.query.get(
            request.form['categoria_id']
        )

        ultimo_producto = Producto.query.filter_by(
            categoria_id=categoria.id
        ).order_by(
            Producto.id.desc()
        ).first()

        if ultimo_producto:

            try:

                ultimo_numero = int(
                    ultimo_producto.codigo.split('_')[-1]
                ) + 1

            except:

                ultimo_numero = 1

        else:

            ultimo_numero = 1

        codigo_generado = (
            f'{categoria.prefijo}_{ultimo_numero:04d}'
        )

        # =========================================
        # CREAR PRODUCTO
        # =========================================

        nuevo_producto = Producto(

            nombre=request.form['nombre'],

            categoria_id=request.form['categoria_id'],

            marca=request.form['marca'],

            descripcion=request.form['descripcion'],

            stock=request.form['stock'],

            stock_minimo=request.form['stock_minimo'],

            precio_compra=request.form['precio_compra'],

            precio_venta=request.form['precio_venta'],

            codigo=codigo_generado,

            foto=foto_nombre

        )

        db.session.add(nuevo_producto)
        db.session.commit()

        flash(
            'Producto registrado correctamente',
            'success'
        )

        return redirect(
            url_for('inventario.listar_productos')
        )

    return render_template(
        'inventario/crear.html',
        categorias=categorias
    )

# =========================================
# VER PRODUCTO
# =========================================

@inventario.route('/ver/<int:id>')
@login_required
@rol_requerido('admin', 'almacen')
def ver_producto(id):

    producto = Producto.query.get_or_404(id)

    return render_template(
        'inventario/ver.html',
        producto=producto
    )

# =========================================
# EDITAR PRODUCTO
# =========================================

@inventario.route('/editar/<int:id>',
                  methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'almacen')
def editar_producto(id):

    producto = Producto.query.get_or_404(id)

    categorias = CategoriaProducto.query.filter_by(
        activo=True
    ).order_by(
        CategoriaProducto.nombre.asc()
    ).all()

    if request.method == 'POST':

        producto.nombre = request.form['nombre']

        producto.categoria_id = request.form['categoria_id']

        producto.marca = request.form['marca']

        producto.stock = request.form['stock']

        producto.stock_minimo = request.form['stock_minimo']

        producto.precio_compra = request.form['precio_compra']

        producto.precio_venta = request.form['precio_venta']

        producto.descripcion = request.form['descripcion']

        # =====================================
        # FOTO
        # =====================================

        foto = request.files.get('foto')

        if foto and foto.filename != '':

            nombre_foto = secure_filename(
                foto.filename
            )

            ruta = os.path.join(
                current_app.root_path,
                'static/uploads/productos',
                nombre_foto
            )

            foto.save(ruta)

            producto.foto = nombre_foto

        db.session.commit()

        flash(
            'Producto actualizado correctamente',
            'success'
        )

        return redirect('/inventario')

    return render_template(
        'inventario/editar.html',
        producto=producto,
        categorias=categorias
    )

# =========================================
# ARCHIVAR PRODUCTO
# =========================================

@inventario.route('/eliminar/<int:id>')
@login_required
@rol_requerido('admin', 'almacen')
def eliminar_producto(id):

    producto = Producto.query.get_or_404(id)

    producto.activo = False

    db.session.commit()

    flash(
        'Producto archivado correctamente',
        'success'
    )

    return redirect(
        url_for('inventario.listar_productos')
    )

# =========================================
# PRODUCTOS ARCHIVADOS
# =========================================

@inventario.route('/archivados')
@login_required
@rol_requerido('admin', 'almacen')
def productos_archivados():

    productos = Producto.query.filter_by(
        activo=False
    ).order_by(
        Producto.id.desc()
    ).all()

    return render_template(
        'inventario/archivados.html',
        productos=productos
    )

# =========================================
# RESTAURAR PRODUCTO
# =========================================

@inventario.route('/restaurar/<int:id>')
@login_required
@rol_requerido('admin', 'almacen')
def restaurar_producto(id):

    producto = Producto.query.get_or_404(id)

    producto.activo = True

    db.session.commit()

    flash(
        'Producto restaurado correctamente',
        'success'
    )

    return redirect(
        url_for('inventario.productos_archivados')
    )