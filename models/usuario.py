from flask_login import UserMixin
from extensions import db
from extensions import login_manager

# =========================================
# MODELO USUARIO
# =========================================

class Usuario(UserMixin, db.Model):

    __tablename__ = 'usuarios'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(150), nullable=False)

    correo = db.Column(db.String(150), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    rol = db.Column(db.String(50), nullable=False, default='tecnico')

    foto = db.Column(db.String(255))

    estado = db.Column(db.Boolean, default=True)

    fecha_creacion = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # =========================================
    # REPRESENTACIÓN
    # =========================================

    def __repr__(self):
        return f'<Usuario {self.nombre}>'
