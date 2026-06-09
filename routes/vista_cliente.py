from flask import (
    Blueprint,
    render_template,
    request
)

from models.orden import Orden

# =========================================
# BLUEPRINT CLIENTE
# =========================================

cliente = Blueprint(
    'cliente',
    __name__,
    url_prefix='/cliente'
)

# =========================================
# CONSULTA CLIENTE
# =========================================

@cliente.route('/consulta', methods=['GET', 'POST'])
def consulta_cliente():

    orden = None

    if request.method == 'POST':

        codigo = request.form['codigo']

        orden = Orden.query.filter_by(
            codigo_orden=codigo
        ).first()

    return render_template(
        'vista_cliente/consulta.html',
        orden=orden
    )