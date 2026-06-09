from extensions import db

# =========================================
# DETALLE VENTA
# =========================================

class DetalleVenta(db.Model):

    __tablename__ = 'detalle_ventas'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    venta_id = db.Column(
        db.Integer,
        db.ForeignKey('ventas.id')
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id')
    )

    cantidad = db.Column(
        db.Integer,
        default=1
    )

    precio_unitario = db.Column(
        db.Float,
        default=0
    )

    subtotal = db.Column(
        db.Float,
        default=0
    )

    # =========================================
    # RELACIONES
    # =========================================

    producto = db.relationship(
        'Producto'
    )

    # =========================================
    # REPRESENTACION
    # =========================================

    def __repr__(self):

        return f'<DetalleVenta {self.id}>'