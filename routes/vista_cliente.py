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
    error = None

    if request.method == 'POST':

        codigo = request.form.get('codigo', '').strip()
        telefono = request.form.get('telefono', '').strip()

        if not codigo or not telefono:
            error = 'Debe ingresar el código y el teléfono.'
        else:
            posible_orden = Orden.query.filter_by(
                codigo_orden=codigo
            ).first()

            # Validar que exista Y que el telefono coincida
            telefono_real = None
            if (posible_orden
                    and posible_orden.equipo
                    and posible_orden.equipo.cliente):
                telefono_real = posible_orden.equipo.cliente.telefono

            # Comparar solo digitos para evitar problemas de formato
            def solo_digitos(t):
                return ''.join(c for c in (t or '') if c.isdigit())

            if (telefono_real
                    and solo_digitos(telefono) == solo_digitos(telefono_real)):
                orden = posible_orden
            else:
                error = (
                    'No se encontró una orden con ese código '
                    'y teléfono. Verifique los datos.'
                )

    return render_template(
        'vista_cliente/consulta.html',
        orden=orden,
        error=error
    )