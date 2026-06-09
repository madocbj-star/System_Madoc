from extensions import db

# =========================================
# REPUESTOS USADOS EN ORDEN
# =========================================

class OrdenRepuesto(db.Model):

    __tablename__ = 'orden_repuestos'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================
    # RELACIONES
    # =========================================

    orden_id = db.Column(
        db.Integer,
        db.ForeignKey('ordenes_servicio.id')
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id')
    )

    # =========================================
    # DATOS
    # =========================================

    cantidad = db.Column(
        db.Integer,
        default=1
    )

    precio = db.Column(
        db.Float,
        default=0
    )

    subtotal = db.Column(
        db.Float,
        default=0
    )

    # =========================================
    # RELACIONES SQLALCHEMY
    # =========================================

    orden = db.relationship(
        'Orden',
        backref='repuestos'
    )

    producto = db.relationship(
        'Producto'
    )

    # =========================================
    # REPRESENTACION
    # =========================================

    def __repr__(self):

        return f'<Repuesto {self.id}>'