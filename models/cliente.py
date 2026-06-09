from extensions import db

# =========================================
# MODELO CLIENTE
# =========================================

class Cliente(db.Model):

    __tablename__ = 'clientes'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    documento = db.Column(
        db.String(50),
        unique=True
    )

    telefono = db.Column(
        db.String(50)
    )

    correo = db.Column(
        db.String(150)
    )

    direccion = db.Column(
        db.String(255)
    )

    empresa = db.Column(
        db.String(150)
    )

    observaciones = db.Column(
        db.Text
    )

    fecha_registro = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # =========================================
    # REPRESENTACIÓN
    # =========================================

    def __repr__(self):

        return f'<Cliente {self.nombre}>'