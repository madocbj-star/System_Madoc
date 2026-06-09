from extensions import db

# =========================================
# MODELO CATEGORIA PRODUCTO
# =========================================

class CategoriaProducto(db.Model):

    __tablename__ = 'categorias_producto'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    prefijo = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    def __repr__(self):

        return f'<CategoriaProducto {self.nombre}>'