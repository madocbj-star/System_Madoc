/* =========================================
   FILTRO EQUIPOS
========================================= */

document.addEventListener('DOMContentLoaded', () => {

    const buscador = document.getElementById(
        'buscadorEquipo'
    )

    const filtroTipo = document.getElementById(
        'filtroTipo'
    )

    const filas = document.querySelectorAll(
        'table tbody tr'
    )

    // =========================================
    // FUNCION FILTRAR
    // =========================================

    function filtrarEquipos() {

        const texto = buscador.value.toLowerCase()

        const tipo = filtroTipo.value.toLowerCase()

        filas.forEach(fila => {

            const contenido = fila.innerText.toLowerCase()

            const tipoFila = fila.children[2]
                .innerText
                .toLowerCase()

            const coincideTexto =
                contenido.includes(texto)

            const coincideTipo =
                tipo === '' ||
                tipoFila.includes(tipo)

            if (coincideTexto && coincideTipo) {

                fila.style.display = ''

            } else {

                fila.style.display = 'none'

            }

        })

    }

    // =========================================
    // EVENTOS
    // =========================================

    buscador.addEventListener(
        'keyup',
        filtrarEquipos
    )

    filtroTipo.addEventListener(
        'change',
        filtrarEquipos
    )

})