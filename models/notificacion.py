from datetime import datetime

from extensions import db


# =========================================
# MODELO NOTIFICACIONES
# =========================================

class Notificacion(db.Model):

    __tablename__ = 'notificaciones'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )

    orden_id = db.Column(
        db.Integer,
        db.ForeignKey('ordenes_servicio.id'),
        nullable=False
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    mensaje = db.Column(
        db.Text,
        nullable=False
    )

    leida = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    # =========================================
    # RELACIONES
    # =========================================

    usuario = db.relationship(
        'Usuario',
        backref='notificaciones'
    )

    orden = db.relationship(
        'Orden',
        backref='notificaciones'
    )

    # =========================================
    # REPRESENTACIÓN
    # =========================================

    def __repr__(self):
        return f'<Notificacion {self.id}>'