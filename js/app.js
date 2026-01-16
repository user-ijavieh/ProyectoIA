const API_URL = 'http://localhost/ProyectoIA/api_pedidos.php';

document.addEventListener('DOMContentLoaded', () => {
    fetchOrders();

    // Auto-refresh every 10 seconds
    setInterval(fetchOrders, 10000);

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        fetchOrders(); // Manual refresh
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
    // Clear columns
    const cols = {
        'pendiente': document.getElementById('list-pendiente'),
        'preparacion': document.getElementById('list-preparacion'),
        'completado': document.getElementById('list-completado')
    };

    const counts = {
        'pendiente': 0,
        'preparacion': 0,
        'completado': 0
    };

    // Reset HTML
    for (const key in cols) {
        cols[key].innerHTML = '';
    }

    orders.forEach(order => {
        const status = order.estado ? order.estado.toLowerCase() : 'pendiente';
        // Fallback for unexpected statuses
        const targetCol = cols[status] || cols['pendiente'];

        if (counts.hasOwnProperty(status)) {
            counts[status]++;
        } else {
            counts['pendiente']++; // Fallback count
        }

        const card = createTicketCard(order);
        targetCol.appendChild(card);
    });

    // Update counts
    document.getElementById('count-pendiente').textContent = counts['pendiente'];
    document.getElementById('count-preparacion').textContent = counts['preparacion'];
    document.getElementById('count-completado').textContent = counts['completado'];
}

function createTicketCard(order) {
    const div = document.createElement('div');
    div.className = `ticket-card status-${order.estado ? order.estado.toLowerCase() : 'pendiente'}`;

    const nextStatusMap = {
        'pendiente': 'preparacion',
        'preparacion': 'completado',
        'completado': null
    };

    const currentStatus = order.estado ? order.estado.toLowerCase() : 'pendiente';
    const nextStatus = nextStatusMap[currentStatus];

    let actionBtnHtml = '';
    if (nextStatus) {
        const btnText = nextStatus === 'preparacion' ? 'Cocinar <i class="fa-solid fa-fire"></i>' : 'Completar <i class="fa-solid fa-check"></i>';
        actionBtnHtml = `<button class="action-btn btn-move-next" onclick="updateStatus('${order.id_pedido}', '${order.producto}', '${nextStatus}')">${btnText}</button>`;
    }

    div.innerHTML = `
        <div class="ticket-header">
            <span class="ticket-id">#${order.id_pedido}</span>
            <span class="ticket-time">${new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <div class="ticket-product">
            <span class="ticket-qty">${order.cantidad}x</span> ${order.producto}
        </div>
        ${order.nota ? `<span class="ticket-note"><i class="fa-regular fa-comment"></i> ${order.nota}</span>` : ''}
        <div class="ticket-actions">
            ${actionBtnHtml}
        </div>
    `;
    return div;
}

async function updateStatus(idPedido, producto, newStatus) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_pedido: idPedido,
                producto: producto,
                estado: newStatus
            })
        });

        const result = await response.json();
        if (result.message) {
            // Refresh board to show changes
            fetchOrders();
        } else {
            alert('Error al actualizar: ' + JSON.stringify(result));
        }

    } catch (error) {
        console.error('Error updating status:', error);
    }
}
