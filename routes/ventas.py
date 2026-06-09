from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
    make_response
)

from reportlab.platypus import ( 
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

import io

from flask_login import login_required

from extensions import db

from models.venta import Venta
from models.producto import Producto
from models.detalle_venta import DetalleVenta
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
        # CODIGO
        # =====================================

        codigo = (
            f'VTA-'
            f'{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )

        # =====================================
        # CREAR VENTA
        # =====================================

        nueva_venta = Venta(

            codigo_venta=codigo,

            cliente_nombre=cliente,

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

            'telefono': cliente.telefono

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

    # =====================================
    # BUFFER
    # =====================================

    buffer = BytesIO()

    doc = SimpleDocTemplate(

        buffer,

        pagesize=letter,

        rightMargin=40,

        leftMargin=40,

        topMargin=40,

        bottomMargin=30

    )

    elementos = []

    estilos = getSampleStyleSheet()

    # =====================================
    # TITULO
    # =====================================

    titulo = Paragraph(

        f"""

        <font size=20>
        <b>FACTURA DE VENTA</b>
        </font>

        <br/><br/>

        Código:
        <b>{venta.codigo_venta}</b>

        <br/>

        Cliente:
        <b>{venta.cliente_nombre}</b>

        <br/>

        Método pago:
        <b>{venta.metodo_pago}</b>

        <br/>

        Fecha:
        <b>
        {venta.fecha_venta.strftime('%Y-%m-%d')}
        </b>

        """,

        estilos['Normal']

    )

    elementos.append(titulo)

    elementos.append(Spacer(1, 25))

    # =====================================
    # TABLA PRODUCTOS
    # =====================================

    data = [

        [

            'Producto',

            'Cantidad',

            'Precio',

            'Subtotal'

        ]

    ]

    for detalle in detalles:

        data.append([

            detalle.producto.nombre,

            detalle.cantidad,

            f"$ {detalle.precio_unitario:,.0f}",

            f"$ {detalle.subtotal:,.0f}"

        ])

    tabla = Table(

        data,

        colWidths=[220, 80, 100, 100]

    )

    tabla.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#38bdf8')),

        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0,0), (-1,0), 12),

        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),

        ('GRID', (0,0), (-1,-1), 1, colors.grey),

        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),

        ('ALIGN', (1,1), (-1,-1), 'CENTER')

    ]))

    elementos.append(tabla)

    elementos.append(Spacer(1, 30))

    # =====================================
    # TOTAL
    # =====================================

    total = Paragraph(

        f"""

        <font size=16>

        <b>

        TOTAL:
        $ {venta.total:,.0f} COP

        </b>

        </font>

        """,

        estilos['Normal']

    )

    elementos.append(total)

    # =====================================
    # GENERAR PDF
    # =====================================

    doc.build(elementos)

    pdf = buffer.getvalue()

    buffer.close()

    response = make_response(pdf)

    response.headers['Content-Type'] = (
        'application/pdf'
    )

    response.headers['Content-Disposition'] = (

        f'inline; filename='
        f'venta_{venta.codigo_venta}.pdf'

    )

    return response
