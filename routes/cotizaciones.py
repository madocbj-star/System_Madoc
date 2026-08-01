from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response,
    current_app
)

from flask_login import login_required, current_user

from weasyprint import HTML

import os
import base64

from datetime import datetime, date

from extensions import db

from models.cotizacion import Cotizacion
from models.detalle_cotizacion import DetalleCotizacion
from models.producto import Producto

from utils.permisos import rol_requerido

cotizaciones = Blueprint(
    'cotizaciones',
    __name__,
    url_prefix='/cotizaciones'
)


# =========================================
# LISTAR COTIZACIONES
# =========================================

@cotizaciones.route('/')
@login_required
@rol_requerido('admin', 'vendedor')
def listar_cotizaciones():

    lista = Cotizacion.query.order_by(
        Cotizacion.id.desc()
    ).all()

    hoy = date.today()

    return render_template(
        'cotizaciones/index.html',
        cotizaciones=lista,
        hoy=hoy
    )


# =========================================
# CREAR COTIZACION
# =========================================

@cotizaciones.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'vendedor')
def crear_cotizacion():

    productos = Producto.query.filter_by(
        activo=True
    ).order_by(
        Producto.nombre.asc()
    ).all()

    if request.method == 'POST':

        data = request.get_json()

        items = data.get('items', [])

        if not items:
            return jsonify({
                'success': False,
                'message': 'Debe agregar al menos un producto o servicio'
            })

        cliente = data.get('cliente')

        if not cliente:
            return jsonify({
                'success': False,
                'message': 'Debe indicar el cliente'
            })

        fecha_vencimiento_str = data.get('fecha_vencimiento')

        if not fecha_vencimiento_str:
            return jsonify({
                'success': False,
                'message': 'Debe indicar la fecha de vigencia'
            })

        try:
            fecha_vencimiento = datetime.strptime(
                fecha_vencimiento_str, '%Y-%m-%d'
            ).date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Fecha de vigencia inválida'
            })

        # =====================================
        # CODIGO (COT_0001, COT_0002, ...)
        # =====================================

        ultima = Cotizacion.query.order_by(
            Cotizacion.id.desc()
        ).first()

        if ultima and ultima.codigo_cotizacion and '_' in ultima.codigo_cotizacion:
            try:
                ultimo_num = int(
                    ultima.codigo_cotizacion.split('_')[-1]
                )
            except ValueError:
                ultimo_num = 0
        else:
            ultimo_num = 0

        codigo = f'COT_{ultimo_num + 1:04d}'

        # =====================================
        # TOTAL
        # =====================================

        subtotal = 0
        for item in items:
            subtotal += float(item['precio_unitario']) * int(item['cantidad'])

        # =====================================
        # CREAR COTIZACION
        # =====================================

        nueva = Cotizacion(
            codigo_cotizacion=codigo,
            cliente_nombre=cliente,
            cliente_documento=data.get('cliente_documento', ''),
            cliente_telefono=data.get('cliente_telefono', ''),
            cliente_correo=data.get('cliente_correo', ''),
            cliente_direccion=data.get('cliente_direccion', ''),
            fecha_vencimiento=fecha_vencimiento,
            estado='pendiente',
            subtotal=subtotal,
            total=subtotal,
            observaciones=data.get('observaciones', ''),
            usuario_id=current_user.id
        )

        db.session.add(nueva)
        db.session.flush()

        for item in items:

            cantidad = int(item['cantidad'])
            precio = float(item['precio_unitario'])

            detalle = DetalleCotizacion(
                cotizacion_id=nueva.id,
                tipo=item.get('tipo', 'producto'),
                producto_id=item.get('producto_id') or None,
                descripcion=item['descripcion'],
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=cantidad * precio
            )

            db.session.add(detalle)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Cotización creada correctamente',
            'id': nueva.id
        })

    return render_template(
        'cotizaciones/crear.html',
        productos=productos
    )


# =========================================
# BUSCAR CLIENTES (reutiliza clientes registrados)
# =========================================

@cotizaciones.route('/buscar-clientes')
@login_required
@rol_requerido('admin', 'vendedor')
def buscar_clientes():

    from models.cliente import Cliente

    texto = request.args.get('q', '')

    clientes = Cliente.query.filter(
        Cliente.nombre.ilike(f'%{texto}%')
    ).limit(10).all()

    resultado = []

    for c in clientes:
        resultado.append({
            'id': c.id,
            'nombre': c.nombre,
            'documento': c.documento,
            'telefono': c.telefono,
            'correo': c.correo,
            'direccion': c.direccion
        })

    return jsonify(resultado)


# =========================================
# VER COTIZACION
# =========================================

@cotizaciones.route('/ver/<int:id>')
@login_required
@rol_requerido('admin', 'vendedor')
def ver_cotizacion(id):

    cotizacion = Cotizacion.query.get_or_404(id)

    hoy = date.today()

    return render_template(
        'cotizaciones/ver.html',
        cotizacion=cotizacion,
        hoy=hoy
    )


# =========================================
# CAMBIAR ESTADO (aceptar / rechazar)
# =========================================

@cotizaciones.route('/cambiar-estado/<int:id>', methods=['POST'])
@login_required
@rol_requerido('admin', 'vendedor')
def cambiar_estado(id):

    cotizacion = Cotizacion.query.get_or_404(id)

    nuevo_estado = request.form.get('estado')

    if nuevo_estado not in ['aceptada', 'rechazada', 'pendiente']:
        flash('Estado no válido', 'danger')
        return redirect(url_for('cotizaciones.ver_cotizacion', id=id))

    cotizacion.estado = nuevo_estado
    db.session.commit()

    flash(f'Cotización marcada como {nuevo_estado}', 'success')

    return redirect(url_for('cotizaciones.ver_cotizacion', id=id))


# =========================================
# PDF DE LA COTIZACION
# =========================================

@cotizaciones.route('/pdf/<int:id>')
@login_required
@rol_requerido('admin', 'vendedor')
def pdf_cotizacion(id):

    cotizacion = Cotizacion.query.get_or_404(id)

    detalles = DetalleCotizacion.query.filter_by(
        cotizacion_id=id
    ).all()

    ruta_css = os.path.join(
        current_app.root_path,
        'static', 'css', 'venta_pdf.css'
    )
    try:
        with open(ruta_css, 'r', encoding='utf-8') as f:
            pdf_css = f.read()
    except FileNotFoundError:
        pdf_css = ''

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
        'pdf/cotizacion_pdf.html',
        cotizacion=cotizacion,
        detalles=detalles,
        pdf_css=pdf_css,
        logo_url=logo_url,
        fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    )

    pdf = HTML(
        string=html,
        base_url=request.host_url
    ).write_pdf()

    response = make_response(pdf)

    response.headers['Content-Type'] = 'application/pdf'

    response.headers['Content-Disposition'] = (
        f'inline; filename={cotizacion.codigo_cotizacion}.pdf'
    )

    return response
