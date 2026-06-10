from app import create_app
from extensions import db

# Modelos
from models.detalle_venta import DetalleVenta
from models.orden_repuesto import OrdenRepuesto
from models.venta import Venta
from models.orden import Orden
from models.equipo import Equipo
from models.producto import Producto
from models.cliente import Cliente

app = create_app()

with app.app_context():

    print("=== INICIANDO REINICIO DE DATOS ===")

    # =========================================
    # ORDEN DE BORRADO (de hijas a padres)
    # =========================================
    # 1. Detalles de venta (dependen de ventas y productos)
    borrados = DetalleVenta.query.delete()
    print(f"Detalles de venta borrados: {borrados}")

    # 2. Repuestos de orden (dependen de ordenes y productos)
    borrados = OrdenRepuesto.query.delete()
    print(f"Repuestos de orden borrados: {borrados}")

    # 3. Ventas
    borrados = Venta.query.delete()
    print(f"Ventas borradas: {borrados}")

    # 4. Ordenes de servicio (dependen de equipos)
    borrados = Orden.query.delete()
    print(f"Ordenes borradas: {borrados}")

    # 5. Equipos (dependen de clientes)
    borrados = Equipo.query.delete()
    print(f"Equipos borrados: {borrados}")

    # 6. Productos del inventario
    borrados = Producto.query.delete()
    print(f"Productos borrados: {borrados}")

    # 7. Clientes
    borrados = Cliente.query.delete()
    print(f"Clientes borrados: {borrados}")

    # Confirmar todos los cambios
    db.session.commit()

    print("=== REINICIO COMPLETADO ===")
    print("Se conservaron: usuario administrador y categorias de productos.")