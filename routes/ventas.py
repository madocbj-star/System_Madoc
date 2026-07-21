from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
    make_response,
    current_app
)

from weasyprint import HTML

import os
import base64

from flask_login import login_required, current_user

from extensions import db

from models.venta import Venta
from models.producto import Producto
from models.detalle_venta import DetalleVenta
from models.movimiento_inventario import MovimientoInventario
from models.cliente import Cliente

from utils.permisos import rol_requerido

from datetime import datetime

# =========================================
# BLUEPRINT
# =========================================

ventas = Blueprint(
    'ventas',
    __name__,
    url_prefix='/ventas'
)

# =========================================
# LISTAR VENTAS
# =========================================

@ventas.route('/')
@login_required
@rol_requerido('admin', 'vendedor')
def listar_ventas():

    lista_ventas = Venta.query.order_by(
        Venta.id.desc()
    ).all()

    return render_template(
        'ventas/index.html',
        ventas=lista_ventas
    )

# =========================================
# CREAR VENTA
# =========================================

@ventas.route('/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin', 'vendedor')
def crear_venta():

    productos = Producto.query.filter_by(
        activo=True
    ).order_by(
        Producto.nombre.asc()
    ).all()

    if request.method == 'POST':

        data = request.get_json()

        carrito = data.get('carrito', [])

        cliente = data.get('cliente')

        cliente_documento = data.get('cliente_documento', '')

        cliente_telefono = data.get('cliente_telefono', '')

        cliente_correo = data.get('cliente_correo', '')

        cliente_direccion = data.get('cliente_direccion', '')

        metodo_pago = data.get('metodo_pago')

        # =====================================
        # VALIDAR
        # =====================================

        if not carrito:

            return jsonify({

                'success': False,
                'message': 'Carrito vacío'

            })

        # =====================================
        # TOTAL
        # =====================================

        subtotal = 0

        for item in carrito:

            subtotal += (
                item['precio']
                * item['cantidad']
            )

        iva = 0

        total = subtotal + iva

        # =====================================
        # CODIGO  (SMA_0001, SMA_0002, ...)
        # =====================================

        ultima_venta = Venta.query.order_by(
            Venta.id.desc()
        ).first()

        if ultima_venta and ultima_venta.codigo_venta and '_' in ultima_venta.codigo_venta:
            try:
                ultimo_num = int(
                    ultima_venta.codigo_venta.split('_')[-1]
                )
            except ValueError:
                ultimo_num = 0
        else:
            ultimo_num = 0

        nuevo_num = ultimo_num + 1

        codigo = f'SMA_{nuevo_num:04d}'

        # =====================================
        # CREAR VENTA
        # =====================================

        nueva_venta = Venta(

            codigo_venta=codigo,

            cliente_nombre=cliente,

            cliente_documento=cliente_documento,

            cliente_telefono=cliente_telefono,

            cliente_correo=cliente_correo,

            cliente_direccion=cliente_direccion,

            metodo_pago=metodo_pago,

            subtotal=subtotal,

            iva=iva,

            total=total

        )

        db.session.add(nueva_venta)

        db.session.flush()

        # =====================================
        # DETALLES
        # =====================================

        for item in carrito:

            producto = Producto.query.get(
                item['id']
            )

            # ================================
            # VALIDAR STOCK
            # ================================

            if producto.stock < item['cantidad']:

                return jsonify({

                    'success': False,

                    'message':
                    f'Stock insuficiente para '
                    f'{producto.nombre}'

                })

            # ================================
            # DESCONTAR STOCK
            # ================================

            producto.stock -= item['cantidad']

            movimiento = MovimientoInventario(
                producto_id=producto.id,
                tipo='salida',
                motivo='venta',
                cantidad=item['cantidad'],
                stock_resultante=producto.stock,
                referencia=f'Venta {nueva_venta.codigo_venta}',
                usuario_id=current_user.id
            )
            db.session.add(movimiento)

            subtotal_item = (
                item['precio']
                * item['cantidad']
            )

            detalle = DetalleVenta(

                venta_id=nueva_venta.id,

                producto_id=producto.id,

                cantidad=item['cantidad'],

                precio_unitario=item['precio'],

                subtotal=subtotal_item

            )

            db.session.add(detalle)

        db.session.commit()

        return jsonify({

            'success': True,

            'message':
            'Venta registrada correctamente'

        })

    return render_template(

        'ventas/crear.html',

        productos=productos

    )

# =========================================
# BUSCAR CLIENTES
# =========================================

@ventas.route('/buscar-clientes')
@login_required
def buscar_clientes():

    texto = request.args.get(
        'q',
        ''
    )

    clientes = Cliente.query.filter(

        Cliente.nombre.ilike(f'%{texto}%')

    ).limit(10).all()

    resultado = []

    for cliente in clientes:

        resultado.append({

            'id': cliente.id,

            'nombre': cliente.nombre,

            'documento': cliente.documento,

            'telefono': cliente.telefono,

            'correo': cliente.correo,

            'direccion': cliente.direccion

        })

    return jsonify(resultado)

# =========================================
# VER VENTA
# =========================================

@ventas.route('/ver/<int:id>')
@login_required
@rol_requerido('admin', 'vendedor')
def ver_venta(id):

    venta = Venta.query.get_or_404(id)

    detalles = DetalleVenta.query.filter_by(
        venta_id=id
    ).all()

    return render_template(

        'ventas/ver.html',

        venta=venta,

        detalles=detalles

    )

# =========================================
# PDF VENTA
# =========================================

@ventas.route('/pdf/<int:id>')
@login_required
@rol_requerido('admin', 'vendedor')
def pdf_venta(id):

    venta = Venta.query.get_or_404(id)

    detalles = DetalleVenta.query.filter_by(
        venta_id=id
    ).all()

    # Leer CSS para incrustarlo
    ruta_css = os.path.join(
        current_app.root_path,
        'static', 'css', 'venta_pdf.css'
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
        'pdf/venta_pdf.html',
        venta=venta,
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
        f'inline; filename=venta_{venta.codigo_venta}.pdf'
    )

    return response
