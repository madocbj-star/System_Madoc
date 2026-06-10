from app import create_app
from extensions import db
from models.usuario import Usuario
from models.categoria_producto import CategoriaProducto
from werkzeug.security import generate_password_hash
import os

app = create_app()

with app.app_context():

    # 1. Crear todas las tablas
    db.create_all()
    print("Tablas creadas correctamente.")

    # 2. Crear usuario administrador si no existe
    correo_admin = "julian99m.jj@gmail.com"
    existe = Usuario.query.filter_by(correo=correo_admin).first()

    if existe:
        print("El usuario administrador ya existe.")
    else:
        admin = Usuario(
            nombre="Julian",
            correo=correo_admin,
            password=generate_password_hash(
                os.environ.get("ADMIN_PASSWORD")
            ),
            rol="admin",
            estado=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado correctamente.")

    # 3. Crear categorías de productos si no existen
    categorias = [
        {"nombre": "Computadores", "prefijo": "PC"},
        {"nombre": "Impresoras", "prefijo": "IMP"},
    ]

    for cat in categorias:
        existe_cat = CategoriaProducto.query.filter_by(
            prefijo=cat["prefijo"]
        ).first()

        if not existe_cat:
            nueva_cat = CategoriaProducto(
                nombre=cat["nombre"],
                prefijo=cat["prefijo"],
                activo=True
            )
            db.session.add(nueva_cat)
            print(f"Categoria {cat['nombre']} creada.")

    db.session.commit()
    print("Categorias verificadas.")