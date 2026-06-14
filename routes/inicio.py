from flask import (
    Blueprint,
    render_template
)

# =========================================
# BLUEPRINT PAGINA PUBLICA (PRESENTACION)
# =========================================

inicio = Blueprint(
    'inicio',
    __name__,
    url_prefix='/inicio'
)


# =========================================
# PAGINA DE PRESENTACION DE LA EMPRESA
# =========================================

@inicio.route('/')
def pagina_inicio():
    return render_template('inicio/landing.html')
