from extensions import db

# =========================================
# MODELO VENTA
# =========================================

class Venta(db.Model):

    __tablename__ = 'ventas'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    codigo_venta = db.Column(
        db.String(100),
        unique=True
    )

    cliente_nombre = db.Column(
        db.String(150),
        nullable=False
    )

    metodo_pago = db.Column(
        db.String(100)
    )

    subtotal = db.Column(
        db.Float,
        default=0
    )

    iva = db.Column(
        db.Float,
        default=0
    )

    total = db.Column(
        db.Float,
        default=0
    )

    fecha_venta = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # =========================================
    # RELACIONES
    # =========================================

    detalles = db.relationship(

        'DetalleVenta',

        backref='venta',

        cascade='all, delete-orphan',

        lazy=True

    )

    # =========================================
    # REPRESENTACION
    # =========================================

    def __repr__(self):

        return f'<Venta {self.codigo_venta}>'