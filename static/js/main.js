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

/* =========================================================
   SYSTEM MADOC - DASHBOARD
   Gráfico de estado de órdenes
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {

    const statusDonut = document.getElementById('statusDonut');

    if (!statusDonut) {
        return;
    }


    /* =====================================================
       OBTENER DATOS DEL DASHBOARD
    ===================================================== */

    const estados = {
        recibido: Number(statusDonut.dataset.recibido) || 0,
        diagnostico: Number(statusDonut.dataset.diagnostico) || 0,
        reparacion: Number(statusDonut.dataset.reparacion) || 0,
        pendiente: Number(statusDonut.dataset.pendiente) || 0,
        listo: Number(statusDonut.dataset.listo) || 0,
        entregado: Number(statusDonut.dataset.entregado) || 0
    };


    /* =====================================================
       TOTAL DE ORDENES
    ===================================================== */

    const total =
        estados.recibido +
        estados.diagnostico +
        estados.reparacion +
        estados.pendiente +
        estados.listo +
        estados.entregado;


    const totalElement = document.getElementById('statusTotal');

    if (totalElement) {
        totalElement.textContent = total;
    }


    /* =====================================================
       ACTUALIZAR VALORES DE LA LEYENDA
    ===================================================== */

    const valores = {
        recibido: estados.recibido,
        diagnostico: estados.diagnostico,
        reparacion: estados.reparacion,
        pendiente: estados.pendiente,
        listo: estados.listo,
        entregado: estados.entregado
    };


    Object.entries(valores).forEach(([estado, valor]) => {

        const elemento = document.querySelector(
            `[data-status-value="${estado}"]`
        );

        if (elemento) {
            elemento.textContent = valor;
        }

    });


    /* =====================================================
       COLORES DEL SISTEMA
       Deben coincidir con style.css
       ===================================================== */

    const colores = {
        recibido: '#0d6efd',
        diagnostico: '#6f42c1',
        reparacion: '#fd7e14',
        pendiente: '#dc3545',
        listo: '#198754',
        entregado: '#6c757d'
    };


    /* =====================================================
       CREAR GRAFICO DONUT
    ===================================================== */

    if (total === 0) {

        statusDonut.style.setProperty(
            '--donut-gradient',
            '#1e293b 0deg 360deg'
        );

        return;
    }


    let gradosActuales = 0;

    const segmentos = [];


    Object.entries(estados).forEach(([estado, cantidad]) => {

        if (cantidad <= 0) {
            return;
        }

        const grados =
            (cantidad / total) * 360;

        const inicio = gradosActuales;

        const fin =
            gradosActuales + grados;

        segmentos.push(
            `${colores[estado]} ${inicio}deg ${fin}deg`
        );

        gradosActuales = fin;

    });


    statusDonut.style.setProperty(
        '--donut-gradient',
        segmentos.join(', ')
    );

});

/* =========================================================
   SYSTEM MADOC - MENU LATERAL RESPONSIVE
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {

    const menuToggle = document.getElementById('madocMenuToggle');
    const sidebar = document.getElementById('madocSidebar');

    if (!menuToggle || !sidebar) {
        return;
    }


    /* =====================================================
       ABRIR / CERRAR SIDEBAR
    ===================================================== */

    menuToggle.addEventListener('click', (event) => {

        event.stopPropagation();

        sidebar.classList.toggle('madoc-sidebar-open');

    });


    /* =====================================================
       CERRAR AL HACER CLICK FUERA DEL SIDEBAR
    ===================================================== */

    document.addEventListener('click', (event) => {

        if (window.innerWidth > 768) {
            return;
        }

        const sidebarAbierto =
            sidebar.classList.contains('madoc-sidebar-open');

        if (!sidebarAbierto) {
            return;
        }

        const clickDentroSidebar =
            sidebar.contains(event.target);

        const clickEnBoton =
            menuToggle.contains(event.target);

        if (!clickDentroSidebar && !clickEnBoton) {

            sidebar.classList.remove(
                'madoc-sidebar-open'
            );

        }

    });


    /* =====================================================
       CERRAR AL SELECCIONAR UNA OPCIÓN
    ===================================================== */

    const sidebarLinks = sidebar.querySelectorAll(
        'a.madoc-sidebar-link'
    );


    sidebarLinks.forEach(link => {

        link.addEventListener('click', () => {

            if (window.innerWidth <= 768) {

                sidebar.classList.remove(
                    'madoc-sidebar-open'
                );

            }

        });

    });


    /* =====================================================
       CERRAR AL CAMBIAR A ESCRITORIO
    ===================================================== */

    window.addEventListener('resize', () => {

        if (window.innerWidth > 768) {

            sidebar.classList.remove(
                'madoc-sidebar-open'
            );

        }

    });

});

/* =========================================================
   SYSTEM MADOC - NOTIFICACIONES REALES
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {

    const notificationButton =
        document.getElementById('madocNotificationButton');

    const notificationPanel =
        document.getElementById('madocNotificationPanel');

    const notificationList =
        document.getElementById('madocNotificationList');

    const notificationBadge =
        document.getElementById('madocNotificationBadge');

    const notificationCount =
        document.getElementById('madocNotificationCount');

    const markNotificationsRead =
        document.getElementById('madocMarkNotificationsRead');


    if (
        !notificationButton ||
        !notificationPanel ||
        !notificationList
    ) {
        return;
    }


    /* =====================================================
       ABRIR / CERRAR PANEL
       ===================================================== */

    notificationButton.addEventListener('click', (event) => {

        event.stopPropagation();

        const abierto =
            notificationPanel.classList.contains('show');

        notificationPanel.classList.toggle('show');

        notificationButton.setAttribute(
            'aria-expanded',
            !abierto
        );

    });


    /* =====================================================
       CERRAR AL HACER CLICK FUERA
       ===================================================== */

    document.addEventListener('click', (event) => {

        const wrapper =
            notificationButton.closest(
                '.madoc-notification-wrapper'
            );

        if (
            wrapper &&
            !wrapper.contains(event.target)
        ) {

            notificationPanel.classList.remove('show');

            notificationButton.setAttribute(
                'aria-expanded',
                'false'
            );

        }

    });


    /* =====================================================
       CARGAR NOTIFICACIONES DESDE FLASK
       ===================================================== */

    async function cargarNotificaciones() {

        try {

            const respuesta =
                await fetch('/ordenes/api/notificaciones');

            if (!respuesta.ok) {
                throw new Error(
                    'No se pudieron cargar las notificaciones'
                );
            }

            const notificaciones =
                await respuesta.json();

            mostrarNotificaciones(notificaciones);

        } catch (error) {

            console.error(
                'Error cargando notificaciones:',
                error
            );

        }

    }


    /* =====================================================
       MOSTRAR NOTIFICACIONES
       ===================================================== */

    function mostrarNotificaciones(notificaciones) {

        notificationList.innerHTML = '';


        if (notificaciones.length === 0) {

            notificationList.innerHTML = `
                <div class="madoc-notification-empty">

                    <i class="bi bi-check-circle"></i>

                    <span>
                        No tienes notificaciones pendientes
                    </span>

                </div>
            `;

            notificationBadge.style.display = 'none';

            notificationCount.textContent =
                '0 pendientes';

            return;
        }


        const cantidad =
            notificaciones.length;


        /* CONTADOR */

        notificationBadge.textContent =
            cantidad;

        notificationBadge.style.display =
            'flex';

        notificationCount.textContent =
            `${cantidad} pendiente${cantidad !== 1 ? 's' : ''}`;


        /* ICONOS */

        notificaciones.forEach(notificacion => {

            let icono = 'bi-bell';

            if (notificacion.tipo === 'nueva_orden') {
                icono = 'bi-tools';
            }

            if (notificacion.tipo === 'cambio_estado') {
                icono = 'bi-arrow-repeat';
            }


            const item =
                document.createElement('div');

            item.className =
                'madoc-notification-item';


            item.innerHTML = `

                <div class="madoc-notification-item-icon">

                    <i class="bi ${icono}"></i>

                </div>

                <div class="madoc-notification-item-content">

                    <strong>
                        ${notificacion.titulo}
                    </strong>

                    <span>
                        ${notificacion.mensaje}
                    </span>

                    <small>
                        ${notificacion.fecha}
                    </small>

                </div>

            `;

            notificationList.appendChild(item);

        });

    }


    /* =====================================================
       MARCAR COMO LEÍDAS
       ===================================================== */

    if (markNotificationsRead) {

        markNotificationsRead.addEventListener(
            'click',
            async (event) => {

                event.stopPropagation();

                try {

                    const respuesta =
                        await fetch(
                            '/ordenes/api/notificaciones/marcar-leidas',
                            {
                                method: 'POST'
                            }
                        );

                    if (!respuesta.ok) {
                        throw new Error(
                            'No se pudieron marcar las notificaciones'
                        );
                    }

                    await cargarNotificaciones();

                } catch (error) {

                    console.error(
                        'Error marcando notificaciones:',
                        error
                    );

                }

            }
        );

    }


    /* =====================================================
       INICIALIZAR
       ===================================================== */

    cargarNotificaciones();

});