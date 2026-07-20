from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    current_app
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
import base64

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

    # =========================================
    # GENERAR ENLACE DE WHATSAPP POR ORDEN
    # =========================================
    import urllib.parse

    enlaces_whatsapp = {}

    for orden in lista_ordenes:

        cliente = None
        if orden.equipo and orden.equipo.cliente:
            cliente = orden.equipo.cliente

        if cliente and cliente.telefono:

            # Limpiar el telefono: solo digitos
            telefono = ''.join(
                c for c in cliente.telefono if c.isdigit()
            )

            # Si no empieza con 57 (Colombia), agregarlo
            if telefono and not telefono.startswith('57'):
                telefono = '57' + telefono

            # Enlace de consulta con el codigo ya puesto
            enlace_consulta = url_for(
                'cliente.consulta_cliente',
                _external=True
            )

            mensaje = (
                f"Hola {cliente.nombre}, le saluda SYSTEM MADOC - "
                f"Soluciones Tecnologicas.\n\n"
                f"Su equipo fue recibido para revision. "
                f"Puede consultar el estado de su reparacion en el "
                f"siguiente enlace:\n{enlace_consulta}\n\n"
                f"Numero de orden: {orden.codigo_orden}\n\n"
                f"Gracias por confiar en nosotros."
            )

            enlaces_whatsapp[orden.id] = (
                f"https://wa.me/{telefono}"
                f"?text={urllib.parse.quote(mensaje)}"
            )
        else:
            enlaces_whatsapp[orden.id] = None

    return render_template(
        'ordenes/index.html',
        ordenes=lista_ordenes,
        enlaces_whatsapp=enlaces_whatsapp
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

        # =========================================
        # EVIDENCIA FOTOGRAFICA (hasta 3 fotos)
        # =========================================
        from utils.cloudinary_helper import subir_imagen_con_id

        for i in [1, 2, 3]:

            campo_foto = request.files.get(f'foto{i}')
            campo_desc = request.form.get(f'foto{i}_desc', '').strip()

            if campo_foto and campo_foto.filename != '':

                url, public_id = subir_imagen_con_id(
                    campo_foto, 'ordenes_evidencia'
                )

                if url:
                    setattr(orden, f'foto{i}_url', url)
                    setattr(orden, f'foto{i}_public_id', public_id)

            if campo_desc:
                setattr(orden, f'foto{i}_desc', campo_desc)

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

    # =========================================
    # LEER EL CSS PARA INCRUSTARLO EN EL PDF
    # =========================================
    ruta_css = os.path.join(
        current_app.root_path,
        'static', 'css', 'pdf.css'
    )

    try:
        with open(ruta_css, 'r', encoding='utf-8') as f:
            pdf_css = f.read()
    except FileNotFoundError:
        pdf_css = ''

    # =========================================
    # LOGO EN BASE64 (para que weasyprint lo lea seguro)
    # =========================================
    ruta_logo = os.path.join(
        current_app.root_path,
        'static', 'img', 'logo2.png'
    )

    try:
        with open(ruta_logo, 'rb') as f:
            logo_b64 = base64.b64encode(f.read()).decode('utf-8')
        logo_url = f'data:image/png;base64,{logo_b64}'
    except FileNotFoundError:
        logo_url = ''

    html = render_template(

        'pdf/orden_pdf.html',

        orden=orden,

        total_repuestos=total_repuestos,

        total_final=total_final,

        fecha_generacion=datetime.now().strftime(
            '%d/%m/%Y %H:%M:%S'
        ),

        pdf_css=pdf_css,

        logo_url=logo_url

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

# =========================================
# GENERAR PDF DE SOPORTE FOTOGRAFICO
# =========================================

@ordenes.route('/soporte-fotografico/<int:id>')
@login_required
@rol_requerido('admin', 'tecnico')
def soporte_fotografico(id):

    orden = Orden.query.get_or_404(id)

    fotos = []
    for i in [1, 2, 3]:
        url = getattr(orden, f'foto{i}_url')
        if url:
            fotos.append({
                'url': url,
                'desc': getattr(orden, f'foto{i}_desc') or ''
            })

    if not fotos:
        flash('Esta orden no tiene fotos de evidencia para generar el soporte.', 'warning')
        return redirect(url_for('ordenes.ver_orden', id=orden.id))

    # Leer CSS (reutilizamos el mismo de la orden)
    ruta_css = os.path.join(
        current_app.root_path,
        'static', 'css', 'pdf.css'
    )
    try:
        with open(ruta_css, 'r', encoding='utf-8') as f:
            pdf_css = f.read()
    except FileNotFoundError:
        pdf_css = ''

    # Logo en base64
    ruta_logo = os.path.join(
        current_app.root_path,
        'static', 'img', 'logo2.png'
    )
    try:
        with open(ruta_logo, 'rb') as f:
            logo_b64 = base64.b64encode(f.read()).decode('utf-8')
        logo_url = f'data:image/png;base64,{logo_b64}'
    except FileNotFoundError:
        logo_url = ''

    html = render_template(
        'pdf/soporte_pdf.html',
        orden=orden,
        fotos=fotos,
        pdf_css=pdf_css,
        logo_url=logo_url,
        fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    )

    pdf = HTML(
        string=html,
        base_url=request.host_url
    ).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        download_name=f'soporte_{orden.codigo_orden}.pdf',
        mimetype='application/pdf'
    )


# =========================================
# LIMPIAR FOTOS DE EVIDENCIA (paso seguro,
# se ejecuta despues de confirmar que el PDF
# de soporte ya quedo descargado)
# =========================================

@ordenes.route('/limpiar-fotos/<int:id>', methods=['POST'])
@login_required
@rol_requerido('admin', 'tecnico')
def limpiar_fotos(id):

    orden = Orden.query.get_or_404(id)

    from utils.cloudinary_helper import eliminar_imagen

    for i in [1, 2, 3]:

        public_id = getattr(orden, f'foto{i}_public_id')

        if public_id:
            eliminar_imagen(public_id)

        setattr(orden, f'foto{i}_url', None)
        setattr(orden, f'foto{i}_public_id', None)
        setattr(orden, f'foto{i}_desc', None)

    db.session.commit()

    flash('Fotos de evidencia eliminadas correctamente.', 'success')

    return redirect(url_for('ordenes.ver_orden', id=orden.id))
