<?php
/**
 * Servicio de lógica de negocio para pedidos
 */

require_once __DIR__ . '/pedidos.repository.php';

class PedidosService {
    private $repository;

    public function __construct($repository) {
        $this->repository = $repository;
    }

    /**
     * Obtiene pedidos según el modo
     * @param string $mode - 'tablero' o 'historial'
     * @return array
     */
    public function obtenerPedidos($mode = 'tablero') {
        if ($mode === 'historial') {
            return $this->repository->obtenerPedidosArchivados();
        }
        
        return $this->repository->obtenerPedidosActivos();
    }

    /**
     * Actualiza el estado de un pedido
     * @param string $idPedido
     * @param string $nuevoEstado
     * @param string $producto - 'ALL' para todo el pedido o nombre específico
     * @return array Respuesta con éxito o error
     */
    public function actualizarEstado($idPedido, $nuevoEstado, $producto = 'ALL') {
        // Validar estados permitidos
        $estadosValidos = ['pendiente', 'preparacion', 'completado', 'archivado'];
        if (!in_array($nuevoEstado, $estadosValidos)) {
            return [
                'success' => false,
                'message' => 'Estado no válido'
            ];
        }

        // Verificar que el pedido existe
        $pedidoExistente = $this->repository->obtenerPedidoPorId($idPedido);
        if (!$pedidoExistente) {
            return [
                'success' => false,
                'message' => 'Pedido no encontrado'
            ];
        }

        // Actualizar según sea todo el pedido o un producto específico
        $resultado = false;
        if ($producto === 'ALL') {
            $resultado = $this->repository->actualizarEstadoCompletoPedido($idPedido, $nuevoEstado);
        } else {
            $resultado = $this->repository->actualizarEstadoProducto($idPedido, $producto, $nuevoEstado);
        }

        return [
            'success' => $resultado,
            'message' => $resultado ? 'Pedido actualizado correctamente' : 'Error al actualizar pedido'
        ];
    }

    /**
     * Crea un nuevo pedido
     * @param array $datos - Array con los datos del pedido
     * @return array
     */
    public function crearNuevoPedido($datos) {
        $requeridos = ['id_pedido', 'producto', 'cantidad'];
        
        // Validar campos requeridos
        foreach ($requeridos as $campo) {
            if (!isset($datos[$campo]) || empty($datos[$campo])) {
                return [
                    'success' => false,
                    'message' => "Campo requerido faltante: $campo"
                ];
            }
        }

        $nota = isset($datos['nota']) ? $datos['nota'] : 'Sin notas';
        $precio = isset($datos['precio_unitario']) ? $datos['precio_unitario'] : 0.0;

        $resultado = $this->repository->crearPedido(
            $datos['id_pedido'],
            $datos['producto'],
            $datos['cantidad'],
            $nota,
            $precio
        );

        return [
            'success' => $resultado,
            'message' => $resultado ? 'Pedido creado correctamente' : 'Error al crear pedido',
            'id_pedido' => $datos['id_pedido']
        ];
    }

    /**
     * Obtiene estadísticas de pedidos
     * @return array
     */
    public function obtenerEstadisticas() {
        $activos = $this->repository->obtenerPedidosActivos();
        
        $stats = [
            'total' => count($activos),
            'por_estado' => [
                'pendiente' => 0,
                'preparacion' => 0,
                'completado' => 0
            ]
        ];

        foreach ($activos as $pedido) {
            $estado = $pedido['estado'];
            if (isset($stats['por_estado'][$estado])) {
                $stats['por_estado'][$estado]++;
            }
        }

        return $stats;
    }
}
