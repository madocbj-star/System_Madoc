from extensions import db

# =========================================
# MODELO DETALLE COTIZACION
# (puede ser un producto del inventario
# o una linea de servicio/mano de obra escrita a mano)
# =========================================

class DetalleCotizacion(db.Model):

    __tablename__ = 'detalle_cotizaciones'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cotizacion_id = db.Column(
        db.Integer,
        db.ForeignKey('cotizaciones.id'),
        nullable=False
    )

    # 'producto' o 'servicio'
    tipo = db.Column(
        db.String(20),
        nullable=False,
        default='producto'
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id')
    )

    producto = db.relationship('Producto')

    descripcion = db.Column(
        db.String(255),
        nullable=False
    )

    cantidad = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    precio_unitario = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    subtotal = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    cotizacion = db.relationship(
        'Cotizacion',
        backref='detalles'
    )

    def __repr__(self):
        return f'<DetalleCotizacion {self.descripcion}>'
