from app import create_app
from extensions import db
from models.usuario import Usuario
from werkzeug.security import generate_password_hash
import os

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("Tablas creadas correctamente.")

    # Crear usuario administrador si no existe
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