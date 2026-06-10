/* =========================================
   VENTAS PRO - Sistema POS
========================================= */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================
    // ESTADO DEL CARRITO
    // =========================================

    let carrito = []

    // =========================================
    // BUSCADOR DE PRODUCTOS
    // =========================================

    const buscadorProductos = document.getElementById('buscador-productos')
    const sinResultados = document.getElementById('sin-resultados')

    buscadorProductos.addEventListener('input', () => {

        const texto = buscadorProductos.value.toLowerCase().trim()
        const items = document.querySelectorAll('.producto-item')
        let visibles = 0

        items.forEach(item => {
            const busqueda = item.dataset.busqueda.toLowerCase()
            if (busqueda.includes(texto)) {
                item.style.display = ''
                visibles++
            } else {
                item.style.display = 'none'
            }
        })

        sinResultados.style.display = visibles === 0 ? 'block' : 'none'

    })

    // =========================================
    // TIPO DE CLIENTE
    // =========================================

    const radioRegistrado = document.getElementById('cliente-registrado')
    const radioOcasional = document.getElementById('cliente-ocasional')
    const contenedorRegistrado = document.getElementById('contenedor-cliente-registrado')
    const contenedorOcasional = document.getElementById('contenedor-cliente-ocasional')

    radioRegistrado.addEventListener('change', () => {
        contenedorRegistrado.style.display = 'block'
        contenedorOcasional.style.display = 'none'
    })

    radioOcasional.addEventListener('change', () => {
        contenedorRegistrado.style.display = 'none'
        contenedorOcasional.style.display = 'block'
    })

    // =========================================
    // BUSCADOR DE CLIENTES REGISTRADOS
    // =========================================

    const clienteInput = document.getElementById('cliente-pos')
    const resultadoClientes = document.getElementById('resultado-clientes')
    const clienteNombreFinal = document.getElementById('cliente-nombre-final')

    let timeoutCliente = null

    clienteInput.addEventListener('input', () => {

        clearTimeout(timeoutCliente)
        const texto = clienteInput.value.trim()

        if (texto.length < 2) {
            resultadoClientes.innerHTML = ''
            resultadoClientes.style.display = 'none'
            clienteNombreFinal.value = ''
            return
        }

        timeoutCliente = setTimeout(() => {

            fetch(`/ventas/buscar-clientes?q=${encodeURIComponent(texto)}`)
                .then(r => r.json())
                .then(data => {

                    if (data.length === 0) {
                        resultadoClientes.innerHTML = '<div class="resultado-item text-secondary">Sin resultados</div>'
                        resultadoClientes.style.display = 'block'
                        return
                    }

                    resultadoClientes.innerHTML = data.map(c =>
                        `<div class="resultado-item" data-nombre="${c.nombre}" data-documento="${c.documento || ''}" data-telefono="${c.telefono || ''}" data-correo="${c.correo || ''}" data-direccion="${c.direccion || ''}">
                            <strong>${c.nombre}</strong>
                            <small class="text-secondary ms-2">${c.telefono || ''}</small>
                        </div>`
                    ).join('')

                    resultadoClientes.style.display = 'block'

                    resultadoClientes.querySelectorAll('.resultado-item').forEach(el => {
                        el.addEventListener('click', () => {
                            clienteInput.value = el.dataset.nombre
                            clienteNombreFinal.value = el.dataset.nombre
                            document.getElementById('cliente-documento-final').value = el.dataset.documento
                            document.getElementById('cliente-telefono-final').value = el.dataset.telefono
                            document.getElementById('cliente-correo-final').value = el.dataset.correo
                            document.getElementById('cliente-direccion-final').value = el.dataset.direccion
                            resultadoClientes.innerHTML = ''
                            resultadoClientes.style.display = 'none'
                        })
                    })

                })
                .catch(() => {
                    resultadoClientes.innerHTML = ''
                    resultadoClientes.style.display = 'none'
                })

        }, 300)

    })

    // Cerrar dropdown al hacer click afuera
    document.addEventListener('click', (e) => {
        if (!clienteInput.contains(e.target) && !resultadoClientes.contains(e.target)) {
            resultadoClientes.style.display = 'none'
        }
    })

    // =========================================
    // AGREGAR AL CARRITO
    // =========================================

    document.querySelectorAll('.btn-agregar').forEach(btn => {

        btn.addEventListener('click', () => {

            const id = parseInt(btn.dataset.id)
            const nombre = btn.dataset.nombre
            const precio = parseFloat(btn.dataset.precio)
            const stockMax = parseInt(btn.dataset.stock)

            const existente = carrito.find(i => i.id === id)

            if (existente) {
                if (existente.cantidad >= stockMax) {
                    mostrarAlerta(`Stock máximo disponible: ${stockMax}`, 'warning')
                    return
                }
                existente.cantidad++
            } else {
                carrito.push({ id, nombre, precio, cantidad: 1, stockMax })
            }

            renderCarrito()

        })

    })

    // =========================================
    // RENDERIZAR CARRITO
    // =========================================

    function renderCarrito() {

        const contenedor = document.getElementById('carrito-items')
        const carritoVacio = document.getElementById('carrito-vacio')

        if (carrito.length === 0) {
            carritoVacio.style.display = 'block'
            document.getElementById('subtotal-pos').textContent = '$0'
            document.getElementById('total-pos').textContent = '$0'
            return
        }

        carritoVacio.style.display = 'none'

        // Limpiar items anteriores (dejar solo el carrito-vacio)
        contenedor.querySelectorAll('.carrito-item').forEach(el => el.remove())

        let subtotal = 0

        carrito.forEach(item => {

            subtotal += item.precio * item.cantidad

            const div = document.createElement('div')
            div.className = 'carrito-item d-flex justify-content-between align-items-center mb-2 p-2 rounded'
            div.style.background = 'rgba(255,255,255,0.05)'
            div.innerHTML = `
                <div style="flex:1; min-width:0;">
                    <div class="fw-bold small text-truncate">${item.nombre}</div>
                    <div class="text-secondary small">$${formatNum(item.precio)} c/u</div>
                </div>
                <div class="d-flex align-items-center gap-1 ms-2">
                    <button class="btn btn-sm btn-outline-secondary btn-cantidad py-0 px-1" data-id="${item.id}" data-accion="restar">−</button>
                    <span class="px-1 fw-bold">${item.cantidad}</span>
                    <button class="btn btn-sm btn-outline-secondary btn-cantidad py-0 px-1" data-id="${item.id}" data-accion="sumar">+</button>
                    <button class="btn btn-sm btn-outline-danger btn-quitar py-0 px-1 ms-1" data-id="${item.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <div class="ms-2 fw-bold small text-nowrap">$${formatNum(item.precio * item.cantidad)}</div>
            `
            contenedor.appendChild(div)

        })

        // Eventos +/-/eliminar
        contenedor.querySelectorAll('.btn-cantidad').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id)
                const item = carrito.find(i => i.id === id)
                if (!item) return
                if (btn.dataset.accion === 'sumar') {
                    if (item.cantidad >= item.stockMax) {
                        mostrarAlerta(`Stock máximo: ${item.stockMax}`, 'warning')
                        return
                    }
                    item.cantidad++
                } else {
                    item.cantidad--
                    if (item.cantidad <= 0) carrito = carrito.filter(i => i.id !== id)
                }
                renderCarrito()
            })
        })

        contenedor.querySelectorAll('.btn-quitar').forEach(btn => {
            btn.addEventListener('click', () => {
                carrito = carrito.filter(i => i.id !== parseInt(btn.dataset.id))
                renderCarrito()
            })
        })

        document.getElementById('subtotal-pos').textContent = `$${formatNum(subtotal)}`
        document.getElementById('total-pos').textContent = `$${formatNum(subtotal)}`

    }

    // =========================================
    // FINALIZAR VENTA
    // =========================================

    document.getElementById('btn-finalizar').addEventListener('click', () => {

        if (carrito.length === 0) {
            mostrarAlerta('El carrito está vacío', 'danger')
            return
        }

        // Obtener cliente
        let nombreCliente = 'Cliente ocasional'
        let docCliente = ''
        let telCliente = ''
        let correoCliente = ''
        let dirCliente = ''

        const tipoSeleccionado = document.querySelector('input[name="tipo_cliente"]:checked').value

        if (tipoSeleccionado === 'registrado') {
            const nombre = clienteNombreFinal.value.trim() || clienteInput.value.trim()
            if (!nombre) {
                mostrarAlerta('Selecciona o escribe el nombre del cliente', 'warning')
                return
            }
            nombreCliente = nombre
            docCliente = document.getElementById('cliente-documento-final').value.trim()
            telCliente = document.getElementById('cliente-telefono-final').value.trim()
            correoCliente = document.getElementById('cliente-correo-final').value.trim()
            dirCliente = document.getElementById('cliente-direccion-final').value.trim()
        } else {
            const ocasional = document.getElementById('cliente-ocasional-nombre').value.trim()
            if (!ocasional) {
                mostrarAlerta('Escribe el nombre del cliente', 'warning')
                return
            }
            nombreCliente = ocasional
            docCliente = document.getElementById('cliente-ocasional-documento').value.trim()
            telCliente = document.getElementById('cliente-ocasional-telefono').value.trim()
            correoCliente = document.getElementById('cliente-ocasional-correo').value.trim()
            dirCliente = document.getElementById('cliente-ocasional-direccion').value.trim()
        }

        const metodo = document.getElementById('metodo-pago').value

        const payload = {
            carrito: carrito.map(i => ({
                id: i.id,
                nombre: i.nombre,
                precio: i.precio,
                cantidad: i.cantidad
            })),
            cliente: nombreCliente,
            cliente_documento: docCliente,
            cliente_telefono: telCliente,
            cliente_correo: correoCliente,
            cliente_direccion: dirCliente,
            metodo_pago: metodo
        }

        const btn = document.getElementById('btn-finalizar')
        btn.disabled = true
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...'

        fetch('/ventas/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {

            if (data.success) {
                mostrarAlerta('¡Venta registrada correctamente!', 'success')
                carrito = []
                renderCarrito()
                clienteInput.value = ''
                clienteNombreFinal.value = ''
                document.getElementById('cliente-documento-final').value = ''
                document.getElementById('cliente-telefono-final').value = ''
                document.getElementById('cliente-correo-final').value = ''
                document.getElementById('cliente-direccion-final').value = ''
                document.getElementById('cliente-ocasional-nombre').value = ''
                document.getElementById('cliente-ocasional-documento').value = ''
                document.getElementById('cliente-ocasional-telefono').value = ''
                document.getElementById('cliente-ocasional-correo').value = ''
                document.getElementById('cliente-ocasional-direccion').value = ''
                // Redirigir al historial después de 1.5s
                setTimeout(() => {
                    window.location.href = '/ventas'
                }, 1500)
            } else {
                mostrarAlerta(data.message || 'Error al registrar la venta', 'danger')
                btn.disabled = false
                btn.innerHTML = '<i class="bi bi-cash-stack"></i> Finalizar Venta'
            }

        })
        .catch(() => {
            mostrarAlerta('Error de conexión', 'danger')
            btn.disabled = false
            btn.innerHTML = '<i class="bi bi-cash-stack"></i> Finalizar Venta'
        })

    })

    // =========================================
    // HELPERS
    // =========================================

    function formatNum(n) {
        return Math.round(n).toLocaleString('es-CO')
    }

    function mostrarAlerta(msg, tipo) {
        // Eliminar alerta previa si existe
        const prev = document.getElementById('alerta-pos')
        if (prev) prev.remove()

        const div = document.createElement('div')
        div.id = 'alerta-pos'
        div.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`
        div.style.cssText = 'top:20px; right:20px; z-index:9999; min-width:280px;'
        div.innerHTML = `
            ${msg}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `
        document.body.appendChild(div)
        setTimeout(() => div.remove(), 4000)
    }

})