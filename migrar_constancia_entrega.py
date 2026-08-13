from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():

    print("=== Agregando columnas de constancia de entrega ===")
    print("(esto NO borra ningun dato existente)")

    columnas = [
        "entrega_nombre_receptor VARCHAR(150)",
        "entrega_firma_url VARCHAR(500)",
        "entrega_firma_public_id VARCHAR(255)",
        "entrega_foto_url VARCHAR(500)",
        "entrega_foto_public_id VARCHAR(255)",
    ]

    for col in columnas:
        nombre_col = col.split()[0]
        try:
            db.session.execute(text(
                f"ALTER TABLE ordenes_servicio "
                f"ADD COLUMN IF NOT EXISTS {col}"
            ))
            db.session.commit()
            print(f"Columna '{nombre_col}' lista.")
        except Exception as e:
            db.session.rollback()
            print(f"Aviso con '{nombre_col}': {e}")

    print("=== Migracion completada ===")
