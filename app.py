from flask import Flask
from flask import redirect
from flask import url_for
from extensions import db
from extensions import mail
from extensions import login_manager

import os


# =========================================
# USER LOADER
# =========================================

@login_manager.user_loader
def load_user(user_id):

    from models.usuario import Usuario

    return Usuario.query.get(int(user_id))

# =========================================
# CREAR APP
# =========================================

def create_app():

    app = Flask(__name__)

    app.config.from_object('config')

    db.init_app(app)

    mail.init_app(app)

    login_manager.init_app(app)

    # Configuración login
    login_manager.login_view = 'auth.login'

    # =========================================
    # IMPORTAR BLUEPRINTS
    # =========================================

    from routes.auth import auth
    from routes.clientes import clientes
    from routes.equipos import equipos
    from routes.ordenes import ordenes
    from routes.inventario import inventario
    from routes.ventas import ventas
    from routes.usuarios import usuarios
    from routes.vista_cliente import cliente

    # =========================================
    # REGISTRAR BLUEPRINTS
    # =========================================

    app.register_blueprint(auth)
    app.register_blueprint(clientes)
    app.register_blueprint(equipos)
    app.register_blueprint(ordenes)
    app.register_blueprint(inventario)
    app.register_blueprint(ventas)
    app.register_blueprint(usuarios)
    app.register_blueprint(cliente)

    return app

# =========================================
# EJECUTAR APP
# =========================================

app = create_app()

# =========================================
# RUTA PRINCIPAL
# =========================================

@app.route('/')
def inicio():

    return redirect(
        url_for('auth.login')
    )

if __name__ == '__main__':

    modo_debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'

    app.run(

        host='0.0.0.0',

        port=5000,

        debug=modo_debug

    )
