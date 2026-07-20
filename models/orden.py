from extensions import db
from extensions import login_manager

# =========================================
# MODELO ORDEN DE SERVICIO
# =========================================

class Orden(db.Model):

    __tablename__ = 'ordenes_servicio'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(db.Integer, primary_key=True)

    codigo_orden = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    problema_reportado = db.Column(db.Text, nullable=False)

    diagnostico = db.Column(db.Text)

    solucion = db.Column(db.Text)

    estado = db.Column(
        db.String(50),
        default='Recibido'
    )

    valor_servicio = db.Column(
        db.Numeric(10, 2),
        default=0
    )

    fecha_ingreso = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    fecha_entrega = db.Column(db.DateTime)

    observaciones = db.Column(db.Text)

    # =========================================
    # FOREIGN KEYS
    # =========================================

    equipo_id = db.Column(
        db.Integer,
        db.ForeignKey('equipos.id'),
        nullable=False
    )

    # =========================================
    # RELACIÓN EQUIPO
    # =========================================

    equipo = db.relationship(
        'Equipo',
        backref='ordenes',
        lazy=True
    )

    tecnico_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id')
    )

    # =========================================
    # RELACIONES
    # =========================================

    tecnico = db.relationship(
        'Usuario',
        backref='ordenes_asignadas'
    )

    # =========================================
    # EVIDENCIA FOTOGRAFICA (temporal, hasta 3 fotos)
    # =========================================

    foto1_url = db.Column(db.String(500))
    foto1_public_id = db.Column(db.String(255))
    foto1_desc = db.Column(db.String(255))

    foto2_url = db.Column(db.String(500))
    foto2_public_id = db.Column(db.String(255))
    foto2_desc = db.Column(db.String(255))

    foto3_url = db.Column(db.String(500))
    foto3_public_id = db.Column(db.String(255))
    foto3_desc = db.Column(db.String(255))

    # =========================================
    # REPRESENTACIÓN
    # =========================================

    def __repr__(self):
        return f'<Orden {self.codigo_orden}>'
