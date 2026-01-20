const API_URL = 'php/api_pedidos.php';

document.addEventListener('DOMContentLoaded', () => {
    fetchOrders();
    setInterval(fetchOrders, 10000); // Auto-refresco cada 10s

    document.getElementById('refreshBtn').addEventListener('click', () => {
        fetchOrders();
    });
});

async function fetchOrders() {
    try {
        const response = await fetch(API_URL);
        const orders = await response.json();

        if (orders.error) {
            console.error(orders.error);
            return;
        }

        renderBoard(orders);
    } catch (error) {
        console.error('Error fetching orders:', error);
    }
}

function renderBoard(orders) {
    const cols = {
        'pendiente': document.getElementById('list-pendiente'),
        'preparacion': document.getElementById('list-preparacion'),
        'completado': document.getElementById('list-completado')
    };

    const counts = { 'pendiente': 0, 'preparacion': 0, 'completado': 0 };

    // Limpiar columnas
    for (const key in cols) { cols[key].innerHTML = ''; }

    // 1. AGRUPAR por id_pedido
    const groupedOrders = {};
    orders.forEach(order => {
        if (!groupedOrders[order.id_pedido]) {
            groupedOrders[order.id_pedido] = {
                id_pedido: order.id_pedido,
                estado: order.estado ? order.estado.toLowerCase() : 'pendiente',
                items: []
            };
        }
        groupedOrders[order.id_pedido].items.push(order);
    });

    // 2. RENDERIZAR un solo ticket por grupo
    Object.values(groupedOrders).forEach(ticket => {
        const status = ticket.estado;
        const targetCol = cols[status] || cols['pendiente'];

        if (counts.hasOwnProperty(status)) {
            counts[status]++;
        }

        const card = createTicketCard(ticket);
        targetCol.appendChild(card);
    });

    // Actualizar contadores
    document.getElementById('count-pendiente').textContent = counts['pendiente'];
    document.getElementById('count-preparacion').textContent = counts['preparacion'];
    document.getElementById('count-completado').textContent = counts['completado'];
}

function createTicketCard(ticket) {
    const div = document.createElement('div');
    div.className = `ticket-card status-${ticket.estado}`;

    const nextStatusMap = {
        'pendiente': 'preparacion',
        'preparacion': 'completado',
        'completado': null
    };

    const nextStatus = nextStatusMap[ticket.estado];
    let actionBtnHtml = '';

    if (nextStatus) {
        const btnText = nextStatus === 'preparacion' ? 'Cocinar <i class="fa-solid fa-fire"></i>' : 'Completar <i class="fa-solid fa-check"></i>';
        actionBtnHtml = `<button class="action-btn btn-move-next" onclick="updateTicketStatus('${ticket.id_pedido}', '${nextStatus}')">${btnText}</button>`;
    }

    // Generar lista de productos dentro del ticket
    const itemsHtml = ticket.items.map(item => `
        <div class="ticket-item">
            <div class="ticket-product">
                <span class="ticket-qty">${item.cantidad}x</span> ${item.producto}
            </div>
            ${item.nota && item.nota !== 'Sin notas' ? `<span class="ticket-note"><i class="fa-regular fa-comment"></i> ${item.nota}</span>` : ''}
        </div>
    `).join('<hr class="ticket-divider">');

    div.innerHTML = `
        <div class="ticket-header">
            <span class="ticket-id">#${ticket.id_pedido}</span>
            <span class="ticket-time">${new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div class="ticket-items-container">
            ${itemsHtml}
        </div>
        <div class="ticket-actions">
            ${actionBtnHtml}
        </div>
    `;
    return div;
}

async function updateTicketStatus(idPedido, newStatus) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_pedido: idPedido,
                estado: newStatus,
                producto: 'ALL' // Flag para actualizar todo el grupo
            })
        });

        const result = await response.json();
        if (result.message) {
            fetchOrders();
        } else {
            console.error('Error al actualizar:', result.error);
        }
    } catch (error) {
        console.error('Error en updateTicketStatus:', error);
    }
}