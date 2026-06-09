from functools import wraps

from flask import flash
from flask import redirect

from flask_login import current_user

# =========================================
# DECORADOR ROLES
# =========================================

def rol_requerido(*roles):

    def decorador(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if current_user.rol not in roles:

                flash(
                    'No tienes permisos para acceder',
                    'danger'
                )

                return redirect('/auth/dashboard')

            return func(*args, **kwargs)

        return wrapper

    return decorador