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
