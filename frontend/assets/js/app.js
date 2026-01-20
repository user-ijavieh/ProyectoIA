const API_URL = '../../backend/api/api_pedidos.php';

document.addEventListener('DOMContentLoaded', () => {
    fetchOrders();
    setInterval(fetchOrders, 10000);
});

async function fetchOrders() {
    try {
        const response = await fetch(API_URL);
        const orders = await response.json();
        renderBoard(orders);
    } catch (e) { console.error(e); }
}

function renderBoard(orders) {
    const cols = { 'pendiente': document.getElementById('list-pendiente'), 'preparacion': document.getElementById('list-preparacion'), 'completado': document.getElementById('list-completado') };
    const counts = { 'pendiente': 0, 'preparacion': 0, 'completado': 0 };
    for (const k in cols) cols[k].innerHTML = '';

    const grouped = {};
    orders.forEach(o => {
        if (!grouped[o.id_pedido]) grouped[o.id_pedido] = { id_pedido: o.id_pedido, estado: o.estado.toLowerCase(), fecha: o.fecha, items: [] };
        grouped[o.id_pedido].items.push(o);
    });

    Object.values(grouped).forEach(t => {
        if (counts.hasOwnProperty(t.estado)) {
            counts[t.estado]++;
            cols[t.estado].appendChild(createTicketCard(t));
        }
    });

    document.getElementById('count-pendiente').textContent = counts['pendiente'];
    document.getElementById('count-preparacion').textContent = counts['preparacion'];
    document.getElementById('count-completado').textContent = counts['completado'];
}

function createTicketCard(ticket) {
    const div = document.createElement('div');
    div.className = `ticket-card status-${ticket.estado}`;
    const next = { 'pendiente': 'preparacion', 'preparacion': 'completado', 'completado': 'archivado' }[ticket.estado];
    
    let btnHtml = '';
    if (next) {
        const txt = { 'preparacion': 'Cocinar', 'completado': 'Completar', 'archivado': 'Archivar' }[next];
        btnHtml = `<button class="action-btn" onclick="updateTicketStatus('${ticket.id_pedido}', '${next}')">${txt}</button>`;
    }

    const items = ticket.items.map(i => `<div><b>${i.cantidad}x</b> ${i.producto}<br><small>${i.nota}</small></div>`).join('<hr>');
    div.innerHTML = `<div class="ticket-header">#${ticket.id_pedido}</div>${items}<div class="ticket-actions">${btnHtml}</div>`;
    return div;
}

async function updateTicketStatus(id, est) {
    await fetch(API_URL, { method: 'POST', body: JSON.stringify({ id_pedido: id, estado: est, producto: 'ALL' }) });
    fetchOrders();
}