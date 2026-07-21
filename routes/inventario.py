from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

import os

from datetime import datetime

from extensions import db

from models.producto import Producto
from models.categoria_producto import CategoriaProducto
from models.proveedor import Proveedor
from models.movimiento_inventario import MovimientoInventario

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

            from utils.cloudinary_helper import subir_imagen

            foto_nombre = subir_imagen(foto, 'productos')

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

            from utils.cloudinary_helper import subir_imagen

            url_foto = subir_imagen(foto, 'productos')

            if url_foto:
                producto.foto = url_foto

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

# =========================================
# AGREGAR MERCANCIA (ENTRADA AL KARDEX)
# =========================================

@inventario.route('/agregar-mercancia', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'almacen')
def agregar_mercancia():

    productos = Producto.query.filter_by(
        activo=True
    ).order_by(Producto.nombre.asc()).all()

    proveedores = Proveedor.query.filter_by(
        activo=True
    ).order_by(Proveedor.nombre.asc()).all()

    if request.method == 'POST':

        producto = Producto.query.get_or_404(
            request.form['producto_id']
        )

        cantidad = int(request.form['cantidad'])

        if cantidad <= 0:
            flash('La cantidad debe ser mayor a cero', 'danger')
            return redirect(url_for('inventario.agregar_mercancia'))

        precio_compra = request.form.get('precio_compra') or 0
        proveedor_id = request.form.get('proveedor_id') or None
        numero_factura = request.form.get('numero_factura') or None

        # =====================================
        # SUMAR AL STOCK
        # =====================================
        producto.stock += cantidad

        # Actualizar precio de compra del producto (el mas reciente)
        if precio_compra:
            producto.precio_compra = float(precio_compra)

        # =====================================
        # REGISTRAR MOVIMIENTO (KARDEX)
        # =====================================
        movimiento = MovimientoInventario(
            producto_id=producto.id,
            tipo='entrada',
            motivo='compra',
            cantidad=cantidad,
            stock_resultante=producto.stock,
            precio_unitario=float(precio_compra) if precio_compra else None,
            proveedor_id=proveedor_id,
            numero_factura=numero_factura,
            referencia='Entrada de mercancía',
            usuario_id=current_user.id
        )

        db.session.add(movimiento)
        db.session.commit()

        flash(
            f'Se agregaron {cantidad} unidades a "{producto.nombre}". '
            f'Stock actual: {producto.stock}',
            'success'
        )

        return redirect(url_for('inventario.agregar_mercancia'))

    return render_template(
        'inventario/agregar_mercancia.html',
        productos=productos,
        proveedores=proveedores
    )


# =========================================
# KARDEX GENERAL (todos los movimientos)
# =========================================

@inventario.route('/kardex')
@login_required
@rol_requerido('admin', 'almacen')
def kardex_general():

    producto_id = request.args.get('producto_id', type=int)
    tipo = request.args.get('tipo', '')

    query = MovimientoInventario.query

    if producto_id:
        query = query.filter_by(producto_id=producto_id)

    if tipo in ['entrada', 'salida']:
        query = query.filter_by(tipo=tipo)

    movimientos = query.order_by(
        MovimientoInventario.fecha.desc()
    ).limit(200).all()

    productos = Producto.query.order_by(
        Producto.nombre.asc()
    ).all()

    return render_template(
        'inventario/kardex.html',
        movimientos=movimientos,
        productos=productos,
        producto_id=producto_id,
        tipo=tipo
    )


# =========================================
# KARDEX POR PRODUCTO
# =========================================

@inventario.route('/kardex/producto/<int:id>')
@login_required
@rol_requerido('admin', 'almacen')
def kardex_producto(id):

    producto = Producto.query.get_or_404(id)

    movimientos = MovimientoInventario.query.filter_by(
        producto_id=id
    ).order_by(
        MovimientoInventario.fecha.desc()
    ).all()

    return render_template(
        'inventario/kardex_producto.html',
        producto=producto,
        movimientos=movimientos
    )
