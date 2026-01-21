/**
 * Utilidades para renderizado del tablero Kanban
 */

const BoardRenderer = {
    columns: {
        pendiente: null,
        preparacion: null,
        completado: null
    },

    counters: {
        pendiente: null,
        preparacion: null,
        completado: null
    },

    /**
     * Inicializa las referencias al DOM
     */
    init() {
        this.columns.pendiente = document.getElementById('list-pendiente');
        this.columns.preparacion = document.getElementById('list-preparacion');
        this.columns.completado = document.getElementById('list-completado');

        this.counters.pendiente = document.getElementById('count-pendiente');
        this.counters.preparacion = document.getElementById('count-preparacion');
        this.counters.completado = document.getElementById('count-completado');
    },

    /**
     * Renderiza el tablero completo con los pedidos
     * @param {Array} pedidos - Lista de pedidos
     */
    render(pedidos) {
        this.clearColumns();
        
        const ticketsAgrupados = this.agruparPorTicket(pedidos);
        const contadores = { pendiente: 0, preparacion: 0, completado: 0 };

        Object.values(ticketsAgrupados).forEach(ticket => {
            const estado = ticket.estado.toLowerCase();
            if (this.columns[estado]) {
                contadores[estado]++;
                const card = this.createTicketCard(ticket);
                this.columns[estado].appendChild(card);
            }
        });

        this.updateCounters(contadores);
    },

    /**
     * Agrupa pedidos por ID de ticket
     * @param {Array} pedidos
     * @returns {Object}
     */
    agruparPorTicket(pedidos) {
        const agrupados = {};
        
        pedidos.forEach(pedido => {
            if (!agrupados[pedido.id_pedido]) {
                agrupados[pedido.id_pedido] = {
                    id_pedido: pedido.id_pedido,
                    estado: pedido.estado.toLowerCase(),
                    fecha: pedido.fecha,
                    items: []
                };
            }
            agrupados[pedido.id_pedido].items.push(pedido);
        });

        return agrupados;
    },

    /**
     * Crea un elemento de tarjeta de ticket
     * @param {Object} ticket
     * @returns {HTMLElement}
     */
    createTicketCard(ticket) {
        const card = document.createElement('div');
        card.className = `ticket-card status-${ticket.estado}`;
        card.dataset.ticketId = ticket.id_pedido;

        const header = this.createCardHeader(ticket.id_pedido);
        const items = this.createCardItems(ticket.items);
        const actions = this.createCardActions(ticket.estado, ticket.id_pedido);

        card.appendChild(header);
        card.appendChild(items);
        card.appendChild(actions);

        return card;
    },

    /**
     * Crea el encabezado de la tarjeta
     */
    createCardHeader(idPedido) {
        const header = document.createElement('div');
        header.className = 'ticket-header';
        header.textContent = `#${idPedido}`;
        return header;
    },

    /**
     * Crea la lista de items del pedido
     */
    createCardItems(items) {
        const container = document.createElement('div');
        container.className = 'ticket-items';

        items.forEach((item, index) => {
            if (index > 0) {
                const separator = document.createElement('hr');
                container.appendChild(separator);
            }

            const itemDiv = document.createElement('div');
            itemDiv.className = 'ticket-item';
            
            const cantidad = document.createElement('b');
            cantidad.textContent = `${item.cantidad}x `;
            
            const producto = document.createTextNode(item.producto);
            
            const nota = document.createElement('small');
            nota.textContent = item.nota || 'Sin notas';
            nota.style.display = 'block';

            itemDiv.appendChild(cantidad);
            itemDiv.appendChild(producto);
            itemDiv.appendChild(document.createElement('br'));
            itemDiv.appendChild(nota);

            container.appendChild(itemDiv);
        });

        return container;
    },

    /**
     * Crea los botones de acción
     */
    createCardActions(estado, idPedido) {
        const container = document.createElement('div');
        container.className = 'ticket-actions';

        const transiciones = {
            'pendiente': { siguiente: 'preparacion', texto: 'Cocinar' },
            'preparacion': { siguiente: 'completado', texto: 'Completar' },
            'completado': { siguiente: 'archivado', texto: 'Archivar' }
        };

        const transicion = transiciones[estado];
        if (transicion) {
            const button = document.createElement('button');
            button.className = 'action-btn';
            button.textContent = transicion.texto;
            button.onclick = () => {
                if (window.TicketManager) {
                    window.TicketManager.actualizarEstado(idPedido, transicion.siguiente);
                }
            };
            container.appendChild(button);
        }

        return container;
    },

    /**
     * Limpia todas las columnas
     */
    clearColumns() {
        Object.values(this.columns).forEach(col => {
            if (col) col.innerHTML = '';
        });
    },

    /**
     * Actualiza los contadores de tickets
     */
    updateCounters(contadores) {
        this.counters.pendiente.textContent = contadores.pendiente;
        this.counters.preparacion.textContent = contadores.preparacion;
        this.counters.completado.textContent = contadores.completado;
    }
};
