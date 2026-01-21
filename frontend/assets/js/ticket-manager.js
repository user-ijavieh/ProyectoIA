/**
 * Gestor de operaciones sobre tickets
 */

const TicketManager = {
    refreshInterval: null,
    autoRefreshEnabled: true,
    refreshRate: 10000, // 10 segundos

    /**
     * Inicializa el gestor de tickets
     */
    init() {
        this.setupEventListeners();
        this.cargarPedidos();
        this.iniciarAutoRefresh();
    },

    /**
     * Configura event listeners
     */
    setupEventListeners() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.cargarPedidos());
        }
    },

    /**
     * Carga y renderiza los pedidos
     */
    async cargarPedidos() {
        try {
            const pedidos = await ApiClient.getPedidos('tablero');
            BoardRenderer.render(pedidos);
        } catch (error) {
            console.error('Error al cargar pedidos:', error);
            this.mostrarError('No se pudieron cargar los pedidos');
        }
    },

    /**
     * Actualiza el estado de un ticket
     * @param {string} idPedido
     * @param {string} nuevoEstado
     */
    async actualizarEstado(idPedido, nuevoEstado) {
        try {
            await ApiClient.actualizarEstadoPedido(idPedido, nuevoEstado, 'ALL');
            await this.cargarPedidos(); // Recargar después de actualizar
        } catch (error) {
            console.error('Error al actualizar estado:', error);
            this.mostrarError('No se pudo actualizar el pedido');
        }
    },

    /**
     * Inicia el refresh automático
     */
    iniciarAutoRefresh() {
        if (this.autoRefreshEnabled) {
            this.refreshInterval = setInterval(() => {
                this.cargarPedidos();
            }, this.refreshRate);
        }
    },

    /**
     * Detiene el refresh automático
     */
    detenerAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    },

    /**
     * Muestra un mensaje de error
     */
    mostrarError(mensaje) {
        // TODO: Implementar sistema de notificaciones
        alert(mensaje);
    }
};

// Exponer globalmente para uso en onclick
window.TicketManager = TicketManager;
