from extensions import db

# =========================================
# MODELO PROVEEDOR
# =========================================

class Proveedor(db.Model):

    __tablename__ = 'proveedores'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    nit_documento = db.Column(
        db.String(50)
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

    activo = db.Column(
        db.Boolean,
        default=True
    )

    fecha_registro = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f'<Proveedor {self.nombre}>'
