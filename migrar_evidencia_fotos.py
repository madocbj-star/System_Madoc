from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():

    print("=== Agregando columnas de evidencia fotografica ===")
    print("(esto NO borra ningun dato existente)")

    columnas = [
        "foto1_url VARCHAR(500)",
        "foto1_public_id VARCHAR(255)",
        "foto1_desc VARCHAR(255)",
        "foto2_url VARCHAR(500)",
        "foto2_public_id VARCHAR(255)",
        "foto2_desc VARCHAR(255)",
        "foto3_url VARCHAR(500)",
        "foto3_public_id VARCHAR(255)",
        "foto3_desc VARCHAR(255)",
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
