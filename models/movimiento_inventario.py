from extensions import db

# =========================================
# MODELO MOVIMIENTO DE INVENTARIO (KARDEX)
# =========================================

class MovimientoInventario(db.Model):

    __tablename__ = 'movimientos_inventario'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id'),
        nullable=False
    )

    producto = db.relationship(
        'Producto',
        backref='movimientos'
    )

    # 'entrada' o 'salida'
    tipo = db.Column(
        db.String(20),
        nullable=False
    )

    # compra, venta, repuesto_orden, devolucion_repuesto, ajuste
    motivo = db.Column(
        db.String(50),
        nullable=False
    )

    cantidad = db.Column(
        db.Integer,
        nullable=False
    )

    stock_resultante = db.Column(
        db.Integer,
        nullable=False
    )

    precio_unitario = db.Column(
        db.Float
    )

    proveedor_id = db.Column(
        db.Integer,
        db.ForeignKey('proveedores.id')
    )

    proveedor = db.relationship('Proveedor')

    numero_factura = db.Column(
        db.String(100)
    )

    referencia = db.Column(
        db.String(150)
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id')
    )

    usuario = db.relationship('Usuario')

    fecha = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f'<Movimiento {self.tipo} {self.cantidad} - {self.producto_id}>'
