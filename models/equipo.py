from extensions import db

from extensions import login_manager

# =========================================
# MODELO EQUIPO
# =========================================

class Equipo(db.Model):

    __tablename__ = 'equipos'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(db.Integer, primary_key=True)

    tipo = db.Column(db.String(50), nullable=False)
    # computador / impresora

    marca = db.Column(db.String(100), nullable=False)

    modelo = db.Column(db.String(100))

    serial = db.Column(db.String(150), unique=True)

    estado_fisico = db.Column(db.Text)

    accesorios = db.Column(db.Text)

    password_equipo = db.Column(db.String(255))

    observaciones = db.Column(db.Text)

    foto = db.Column(db.String(255))

    fecha_registro = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # =========================================
    # FOREIGN KEYS
    # =========================================

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey('clientes.id'),
        nullable=False
    )

    cliente = db.relationship(
        'Cliente',
        backref='equipos'
    )

    # =========================================
    # REPRESENTACIÓN
    # =========================================

    def __repr__(self):
        return f'<Equipo {self.marca} {self.modelo}>'
