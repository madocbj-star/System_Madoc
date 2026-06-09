import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# =========================================
# CONFIGURACIÓN POSTGRESQL
# =========================================

# Render entrega DATABASE_URL completa; si existe, la usamos
database_url = os.environ.get('DATABASE_URL')

if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
else:
    # Conexión local (cuando trabajas en tu computador)
    usuario = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    puerto = os.environ.get('DB_PORT')
    database = os.environ.get('DB_NAME')

    password_codificado = urllib.parse.quote_plus(password)

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{usuario}:{password_codificado}'
        f'@{host}:{puerto}/{database}'
    )

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get('SECRET_KEY')

# =========================================
# CONFIGURACIÓN MAIL
# =========================================

MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')