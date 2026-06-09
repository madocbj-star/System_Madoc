from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from flask_login import login_required
from utils.permisos import rol_requerido

from extensions import db	

from models.orden import Orden
from models.equipo import Equipo
from models.usuario import Usuario
from models.producto import Producto
from models.orden_repuesto import OrdenRepuesto

from datetime import datetime

import os
import io

from weasyprint import HTML

# =========================================
# CREAR BLUEPRINT
# =========================================

ordenes = Blueprint(
    'ordenes',
    __name__,
    url_prefix='/ordenes'
)

# =========================================
# LISTAR ÓRDENES
# =========================================

@ordenes.route('/')
@login_required
@rol_requerido('admin', 'tecnico')
def listar_ordenes():

    lista_ordenes = Orden.query.order_by(
        Orden.id.desc()
    ).all()

    return render_template(
        'ordenes/index.html',
        ordenes=lista_ordenes
    )

# =========================================
# CREAR ORDEN
# =========================================

@ordenes.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'tecnico')
def crear_orden():

    equipos = Equipo.query.order_by(Equipo.id.desc()).all()

    # Solo técnicos y admins activos
    tecnicos = Usuario.query.filter(
        Usuario.rol.in_(['admin', 'tecnico']),
        Usuario.estado == True
    ).order_by(Usuario.nombre.asc()).all()

    if request.method == 'POST':

        # Consecutivo robusto usando el max id
        from sqlalchemy import func
        max_id = db.session.query(func.max(Orden.id)).scalar() or 0
        codigo = f'SER-JUL-{max_id + 1:04d}'

        tecnico_id = request.form.get('tecnico_id') or None

        nueva_orden = Orden(

            codigo_orden=codigo,

            problema_reportado=request.form[
                'problema_reportado'
            ],

            diagnostico=request.form[
                'diagnostico'
            ],

            solucion=request.form[
                'solucion'
            ],

            estado=request.form[
                'estado'
            ],

            valor_servicio=request.form[
                'valor_servicio'
            ],

            observaciones=request.form[
                'observaciones'
            ],

            equipo_id=request.form[
                'equipo_id'
            ],

            tecnico_id=tecnico_id

        )

        db.session.add(nueva_orden)
        db.session.commit()

        flash('Orden creada correctamente', 'success')

        return redirect(url_for('ordenes.listar_ordenes'))

    return render_template(
        'ordenes/crear.html',
        equipos=equipos,
        tecnicos=tecnicos
    )

# =========================================
# VER ORDEN
# =========================================

@ordenes.route('/ver/<int:id>')
@login_required
@rol_requerido('admin', 'tecnico')
def ver_orden(id):

    orden = Orden.query.get_or_404(id)

    productos = Producto.query.order_by(
        Producto.nombre.asc()
    ).all()

    total_repuestos = sum(
        repuesto.subtotal
        for repuesto in orden.repuestos
    )

    total_final = (
        float(orden.valor_servicio)
        + total_repuestos
    )

    return render_template(
        'ordenes/ver.html',
        orden=orden,
        productos=productos,
        total_repuestos=total_repuestos,
        total_final=total_final
    )

# =========================================
# EDITAR ORDEN
# =========================================

@ordenes.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'tecnico')
def editar_orden(id):

    orden = Orden.query.get_or_404(id)

    tecnicos = Usuario.query.filter(
        Usuario.rol.in_(['admin', 'tecnico']),
        Usuario.estado == True
    ).order_by(Usuario.nombre.asc()).all()

    if request.method == 'POST':

        orden.estado = request.form['estado']

        orden.problema_reportado = request.form[
            'problema_reportado'
        ]

        orden.diagnostico = request.form[
            'diagnostico'
        ]

        orden.solucion = request.form[
            'solucion'
        ]

        orden.valor_servicio = request.form[
            'valor_servicio'
        ]

        orden.observaciones = request.form[
            'observaciones'
        ]

        orden.tecnico_id = request.form.get('tecnico_id') or None

        db.session.commit()

        flash('Orden actualizada correctamente', 'success')

        return redirect(
            url_for('ordenes.ver_orden', id=orden.id)
        )

    return render_template(
        'ordenes/editar.html',
        orden=orden,
        tecnicos=tecnicos
    )

# =========================================
# PDF ORDEN
# =========================================

@ordenes.route('/pdf/<int:id>')
@login_required
@rol_requerido('admin', 'tecnico')
def pdf_orden(id):

    orden = Orden.query.get_or_404(id)

    total_repuestos = sum(
        repuesto.subtotal
        for repuesto in orden.repuestos
    )

    total_final = (
        float(orden.valor_servicio) + total_repuestos
    )

    html = render_template(

        'pdf/orden_pdf.html',

        orden=orden,

        total_repuestos=total_repuestos,

        total_final=total_final,

        fecha_generacion=datetime.now().strftime(
            '%d/%m/%Y %H:%M:%S'
        ),

        os=os

    )

    pdf = HTML(
        string=html,
        base_url=request.host_url
    ).write_pdf()

    return send_file(

        io.BytesIO(pdf),

        download_name=f'{orden.codigo_orden}.pdf',

        mimetype='application/pdf',

        as_attachment=True

    )

# =========================================
# AGREGAR REPUESTO
# =========================================

@ordenes.route('/agregar-repuesto/<int:id>', methods=['POST'])
@login_required
@rol_requerido('admin', 'tecnico')
def agregar_repuesto(id):

    orden = Orden.query.get_or_404(id)

    producto = Producto.query.get_or_404(
        request.form['producto_id']
    )

    cantidad = int(request.form['cantidad'])

    if producto.stock < cantidad:

        flash('Stock insuficiente', 'danger')

        return redirect(
            url_for('ordenes.ver_orden', id=orden.id)
        )

    producto.stock -= cantidad

    subtotal = producto.precio_venta * cantidad

    nuevo_repuesto = OrdenRepuesto(

        orden_id=orden.id,

        producto_id=producto.id,

        cantidad=cantidad,

        precio=producto.precio_venta,

        subtotal=subtotal

    )

    db.session.add(nuevo_repuesto)
    db.session.commit()

    flash('Repuesto agregado correctamente', 'success')

    return redirect(
        url_for('ordenes.ver_orden', id=orden.id)
    )

# =========================================
# ELIMINAR REPUESTO
# =========================================

@ordenes.route('/eliminar-repuesto/<int:id>')
@login_required
@rol_requerido('admin', 'tecnico')
def eliminar_repuesto(id):

    repuesto = OrdenRepuesto.query.get_or_404(id)

    producto = Producto.query.get(repuesto.producto_id)

    if producto:
        producto.stock += repuesto.cantidad

    orden_id = repuesto.orden_id

    db.session.delete(repuesto)
    db.session.commit()

    flash('Repuesto eliminado correctamente', 'success')

    return redirect(
        url_for('ordenes.ver_orden', id=orden_id)
    )
