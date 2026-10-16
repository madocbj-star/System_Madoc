document.addEventListener('DOMContentLoaded', function () {

    const inputFoto = document.getElementById('fotoEquipo');
    const vistaPrevia = document.getElementById('vistaPreviaFoto');
    const sinFoto = document.getElementById('sinFoto');

    if (!inputFoto || !vistaPrevia) {
        return;
    }

    inputFoto.addEventListener('change', function () {

        const archivo = this.files[0];

        if (!archivo) {
            return;
        }

        if (!archivo.type.startsWith('image/')) {
            alert('Selecciona un archivo de imagen válido.');
            this.value = '';
            return;
        }

        vistaPrevia.src = URL.createObjectURL(archivo);
        vistaPrevia.classList.remove('d-none');

        if (sinFoto) {
            sinFoto.classList.add('d-none');
        }
    });

});