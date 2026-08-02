from flask import (
    Blueprint,
    render_template,
    request
)
from flask_login import login_required
from utils.permisos import rol_requerido
from extensions import db
from models.venta import Venta
from models.detalle_venta import DetalleVenta
from models.producto import Producto
from models.orden import Orden
from models.orden_repuesto import OrdenRepuesto
from models.usuario import Usuario
from sqlalchemy import func, extract
from datetime import datetime
import calendar

# =========================================
# BLUEPRINT REPORTES (solo admin)
# =========================================

reportes = Blueprint(
    'reportes',
    __name__,
    url_prefix='/reportes'
)


@reportes.route('/ventas')
@login_required
@rol_requerido('admin')
def reporte_ventas():

    # =====================================
    # MES Y AÑO SELECCIONADO
    # =====================================
    hoy = datetime.now()

    try:
        mes = int(request.args.get('mes', hoy.month))
        anio = int(request.args.get('anio', hoy.year))
    except ValueError:
        mes = hoy.month
        anio = hoy.year

    # Validar rango
    if mes < 1 or mes > 12:
        mes = hoy.month

    # =====================================
    # VENTAS DEL MES SELECCIONADO
    # =====================================
    ventas_mes = Venta.query.filter(
        extract('month', Venta.fecha_venta) == mes,
        extract('year', Venta.fecha_venta) == anio
    ).order_by(Venta.fecha_venta.desc()).all()

    # =====================================
    # NUMEROS CLAVE
    # =====================================
    total_vendido = sum(float(v.total) for v in ventas_mes)
    cantidad_ventas = len(ventas_mes)
    promedio_venta = (
        total_vendido / cantidad_ventas
        if cantidad_ventas > 0 else 0
    )

    # =====================================
    # VENTAS POR DIA (para el grafico)
    # =====================================
    dias_en_mes = calendar.monthrange(anio, mes)[1]
    ventas_por_dia = {d: 0 for d in range(1, dias_en_mes + 1)}

    for v in ventas_mes:
        dia = v.fecha_venta.day
        ventas_por_dia[dia] += float(v.total)

    # Listas para el grafico
    dias_labels = list(ventas_por_dia.keys())
    dias_valores = list(ventas_por_dia.values())

    # =====================================
    # PRODUCTOS MAS VENDIDOS DEL MES
    # =====================================
    ids_ventas = [v.id for v in ventas_mes]

    productos_top = []
    if ids_ventas:
        resultado = db.session.query(
            Producto.nombre,
            func.sum(DetalleVenta.cantidad).label('total_cantidad'),
            func.sum(DetalleVenta.subtotal).label('total_dinero')
        ).join(
            DetalleVenta, DetalleVenta.producto_id == Producto.id
        ).filter(
            DetalleVenta.venta_id.in_(ids_ventas)
        ).group_by(
            Producto.nombre
        ).order_by(
            func.sum(DetalleVenta.cantidad).desc()
        ).limit(5).all()

        productos_top = [
            {
                'nombre': r[0],
                'cantidad': int(r[1]),
                'dinero': float(r[2])
            }
            for r in resultado
        ]

    # =====================================
    # NOMBRE DEL MES EN ESPAÑOL
    # =====================================
    meses_es = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril',
        'Mayo', 'Junio', 'Julio', 'Agosto',
        'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    nombre_mes = meses_es[mes]

    # Años disponibles para el selector (de 2025 al actual)
    anios_disponibles = list(range(2025, hoy.year + 1))

    return render_template(
        'reportes/ventas.html',
        ventas=ventas_mes,
        total_vendido=total_vendido,
        cantidad_ventas=cantidad_ventas,
        promedio_venta=promedio_venta,
        dias_labels=dias_labels,
        dias_valores=dias_valores,
        productos_top=productos_top,
        mes=mes,
        anio=anio,
        nombre_mes=nombre_mes,
        meses_es=meses_es,
        anios_disponibles=anios_disponibles
    )


@reportes.route('/servicios')
@login_required
@rol_requerido('admin')
def reporte_servicios():

    # =====================================
    # MES Y AÑO SELECCIONADO
    # =====================================
    hoy = datetime.now()

    try:
        mes = int(request.args.get('mes', hoy.month))
        anio = int(request.args.get('anio', hoy.year))
    except ValueError:
        mes = hoy.month
        anio = hoy.year

    if mes < 1 or mes > 12:
        mes = hoy.month

    # =====================================
    # ORDENES ENTREGADAS, AGRUPADAS POR
    # FECHA DE INGRESO (cuando se recibio el equipo)
    # =====================================
    ordenes_mes = Orden.query.filter(
        Orden.estado == 'ENTREGADO',
        extract('month', Orden.fecha_ingreso) == mes,
        extract('year', Orden.fecha_ingreso) == anio
    ).order_by(Orden.fecha_ingreso.desc()).all()

    # =====================================
    # CALCULAR TOTAL POR ORDEN (servicio + repuestos)
    # =====================================
    ordenes_detalle = []
    total_facturado = 0

    for orden in ordenes_mes:

        total_repuestos = sum(
            float(r.subtotal) for r in orden.repuestos
        )
        total_orden = float(orden.valor_servicio or 0) + total_repuestos

        total_facturado += total_orden

        ordenes_detalle.append({
            'orden': orden,
            'total': total_orden
        })

    cantidad_ordenes = len(ordenes_mes)
    promedio_orden = (
        total_facturado / cantidad_ordenes
        if cantidad_ordenes > 0 else 0
    )

    # =====================================
    # ORDENES POR DIA (para el grafico)
    # =====================================
    dias_en_mes = calendar.monthrange(anio, mes)[1]
    ordenes_por_dia = {d: 0 for d in range(1, dias_en_mes + 1)}

    for item in ordenes_detalle:
        dia = item['orden'].fecha_ingreso.day
        ordenes_por_dia[dia] += item['total']

    dias_labels = list(ordenes_por_dia.keys())
    dias_valores = list(ordenes_por_dia.values())

    # =====================================
    # RANKING DE TECNICOS (quien hizo mas servicios)
    # =====================================
    conteo_tecnicos = {}

    for item in ordenes_detalle:
        orden = item['orden']
        tecnico = orden.tecnico.nombre if orden.tecnico else 'Sin asignar'

        if tecnico not in conteo_tecnicos:
            conteo_tecnicos[tecnico] = {'cantidad': 0, 'total': 0}

        conteo_tecnicos[tecnico]['cantidad'] += 1
        conteo_tecnicos[tecnico]['total'] += item['total']

    ranking_tecnicos = sorted(
        [
            {'nombre': k, 'cantidad': v['cantidad'], 'total': v['total']}
            for k, v in conteo_tecnicos.items()
        ],
        key=lambda x: x['cantidad'],
        reverse=True
    )

    # =====================================
    # NOMBRE DEL MES Y AÑOS DISPONIBLES
    # =====================================
    meses_es = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril',
        'Mayo', 'Junio', 'Julio', 'Agosto',
        'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    nombre_mes = meses_es[mes]
    anios_disponibles = list(range(2025, hoy.year + 1))

    return render_template(
        'reportes/servicios.html',
        ordenes_detalle=ordenes_detalle,
        total_facturado=total_facturado,
        cantidad_ordenes=cantidad_ordenes,
        promedio_orden=promedio_orden,
        dias_labels=dias_labels,
        dias_valores=dias_valores,
        ranking_tecnicos=ranking_tecnicos,
        mes=mes,
        anio=anio,
        nombre_mes=nombre_mes,
        meses_es=meses_es,
        anios_disponibles=anios_disponibles
    )
