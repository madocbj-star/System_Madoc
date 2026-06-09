from extensions import db

# =========================================
# MODELO PRODUCTO
# =========================================

class Producto(db.Model):

    __tablename__ = 'productos'

    # =========================================
    # COLUMNAS
    # =========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey('categorias_producto.id')
    )

    categoria = db.relationship(
        'CategoriaProducto',
        backref='productos'
    )

    marca = db.Column(
        db.String(100)
    )

    descripcion = db.Column(
        db.Text
    )

    stock = db.Column(
        db.Integer,
        default=0
    )

    stock_minimo = db.Column(
        db.Integer,
        default=1
    )

    precio_compra = db.Column(
        db.Float,
        default=0
    )

    precio_venta = db.Column(
        db.Float,
        default=0
    )

    codigo = db.Column(
        db.String(100),
        unique=True
    )

    foto = db.Column(
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

    # =========================================
    # REPRESENTACIÓN
    # =========================================

    def __repr__(self):

        return f'<Producto {self.nombre}>'