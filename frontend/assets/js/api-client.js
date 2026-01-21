/**
 * Cliente API para comunicación con el backend
 */

const API_BASE_URL = '../../backend/api';

const ApiClient = {
    /**
     * Obtiene la lista de pedidos
     * @param {string} mode - 'tablero' o 'historial'
     * @returns {Promise<Array>}
     */
    async getPedidos(mode = 'tablero') {
        try {
            const url = mode === 'historial' 
                ? `${API_BASE_URL}/pedidos.controller.php?mode=historial`
                : `${API_BASE_URL}/pedidos.controller.php`;
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Error al obtener pedidos');
            return await response.json();
        } catch (error) {
            console.error('Error en getPedidos:', error);
            throw error;
        }
    },

    /**
     * Actualiza el estado de un pedido
     * @param {string} idPedido - ID del ticket
     * @param {string} nuevoEstado - Nuevo estado del pedido
     * @param {string} producto - Producto específico o 'ALL'
     * @returns {Promise<Object>}
     */
    async actualizarEstadoPedido(idPedido, nuevoEstado, producto = 'ALL') {
        try {
            const response = await fetch(`${API_BASE_URL}/pedidos.controller.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id_pedido: idPedido,
                    estado: nuevoEstado,
                    producto: producto
                })
            });
            
            if (!response.ok) throw new Error('Error al actualizar pedido');
            return await response.json();
        } catch (error) {
            console.error('Error en actualizarEstadoPedido:', error);
            throw error;
        }
    }
};

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiClient;
}
