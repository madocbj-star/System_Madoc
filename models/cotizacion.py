from extensions import db

# =========================================
# MODELO COTIZACION
# =========================================

class Cotizacion(db.Model):

    __tablename__ = 'cotizaciones'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    codigo_cotizacion = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    # =========================================
    # DATOS DEL CLIENTE (registrado u ocasional)
    # =========================================

    cliente_nombre = db.Column(
        db.String(150),
        nullable=False
    )

    cliente_documento = db.Column(db.String(50))
    cliente_telefono = db.Column(db.String(50))
    cliente_correo = db.Column(db.String(150))
    cliente_direccion = db.Column(db.String(255))

    # =========================================
    # FECHAS
    # =========================================

    fecha_cotizacion = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    fecha_vencimiento = db.Column(
        db.Date,
        nullable=False
    )

    # =========================================
    # ESTADO: pendiente / aceptada / rechazada
    # =========================================

    estado = db.Column(
        db.String(20),
        default='pendiente'
    )

    # =========================================
    # VALORES
    # =========================================

    subtotal = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)

    observaciones = db.Column(db.Text)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id')
    )

    usuario = db.relationship('Usuario')

    def __repr__(self):
        return f'<Cotizacion {self.codigo_cotizacion}>'
