import os
import cloudinary
import cloudinary.uploader

# =========================================
# CONFIGURACIÓN CLOUDINARY
# =========================================

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

# =========================================
# FUNCIÓN PARA SUBIR IMÁGENES
# =========================================

def subir_imagen(archivo, carpeta):
    """
    Sube una imagen a Cloudinary y devuelve la URL permanente.
    archivo: el archivo recibido del formulario (request.files)
    carpeta: subcarpeta en Cloudinary, ej: 'usuarios', 'equipos', 'productos'
    """
    if not archivo or archivo.filename == '':
        return None

    resultado = cloudinary.uploader.upload(
        archivo,
        folder=f'system_madoc/{carpeta}'
    )

    return resultado.get('secure_url')


def subir_imagen_con_id(archivo, carpeta):
    """
    Sube una imagen a Cloudinary y devuelve (url, public_id).
    El public_id se necesita para poder borrar la imagen despues.
    """
    if not archivo or archivo.filename == '':
        return None, None

    resultado = cloudinary.uploader.upload(
        archivo,
        folder=f'system_madoc/{carpeta}'
    )

    return resultado.get('secure_url'), resultado.get('public_id')


def eliminar_imagen(public_id):
    """
    Elimina una imagen de Cloudinary usando su public_id.
    No falla si la imagen ya no existe.
    """
    if not public_id:
        return

    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass