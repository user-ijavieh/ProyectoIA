<?php
/**
 * Repositorio de datos para pedidos
 * Maneja todas las operaciones de base de datos
 */

class PedidosRepository {
    private $conn;

    public function __construct($connection) {
        $this->conn = $connection;
    }

    /**
     * Obtiene pedidos activos (no archivados)
     * @return array
     */
    public function obtenerPedidosActivos() {
        $sql = "SELECT * FROM pedidos WHERE estado != 'archivado' ORDER BY id DESC";
        $result = $this->conn->query($sql);
        
        $pedidos = [];
        if ($result) {
            while($row = $result->fetch_assoc()) {
                $pedidos[] = $row;
            }
        }
        
        return $pedidos;
    }

    /**
     * Obtiene pedidos archivados
     * @return array
     */
    public function obtenerPedidosArchivados() {
        $sql = "SELECT * FROM pedidos WHERE estado = 'archivado' ORDER BY fecha DESC";
        $result = $this->conn->query($sql);
        
        $pedidos = [];
        if ($result) {
            while($row = $result->fetch_assoc()) {
                $pedidos[] = $row;
            }
        }
        
        return $pedidos;
    }

    /**
     * Actualiza el estado de todos los items de un pedido
     * @param string $idPedido
     * @param string $nuevoEstado
     * @return bool
     */
    public function actualizarEstadoCompletoPedido($idPedido, $nuevoEstado) {
        $idPedido = $this->conn->real_escape_string($idPedido);
        $nuevoEstado = $this->conn->real_escape_string($nuevoEstado);
        
        $sql = "UPDATE pedidos 
                SET estado = '$nuevoEstado', fecha = NOW() 
                WHERE id_pedido = '$idPedido'";
        
        return $this->conn->query($sql);
    }

    /**
     * Actualiza el estado de un producto específico de un pedido
     * @param string $idPedido
     * @param string $producto
     * @param string $nuevoEstado
     * @return bool
     */
    public function actualizarEstadoProducto($idPedido, $producto, $nuevoEstado) {
        $idPedido = $this->conn->real_escape_string($idPedido);
        $producto = $this->conn->real_escape_string($producto);
        $nuevoEstado = $this->conn->real_escape_string($nuevoEstado);
        
        $sql = "UPDATE pedidos 
                SET estado = '$nuevoEstado', fecha = NOW() 
                WHERE id_pedido = '$idPedido' AND producto = '$producto'";
        
        return $this->conn->query($sql);
    }

    /**
     * Obtiene un pedido específico por ID
     * @param string $idPedido
     * @return array|null
     */
    public function obtenerPedidoPorId($idPedido) {
        $idPedido = $this->conn->real_escape_string($idPedido);
        
        $sql = "SELECT * FROM pedidos WHERE id_pedido = '$idPedido'";
        $result = $this->conn->query($sql);
        
        $items = [];
        if ($result) {
            while($row = $result->fetch_assoc()) {
                $items[] = $row;
            }
        }
        
        return empty($items) ? null : $items;
    }

    /**
     * Crea un nuevo pedido
     * @param string $idPedido
     * @param string $producto
     * @param int $cantidad
     * @param string $nota
     * @param float $precioUnitario
     * @return bool
     */
    public function crearPedido($idPedido, $producto, $cantidad, $nota, $precioUnitario = 0.0) {
        $idPedido = $this->conn->real_escape_string($idPedido);
        $producto = $this->conn->real_escape_string($producto);
        $cantidad = (int)$cantidad;
        $nota = $this->conn->real_escape_string($nota);
        $precioUnitario = (float)$precioUnitario;
        
        $sql = "INSERT INTO pedidos (id_pedido, producto, cantidad, nota, precio_unitario, estado) 
                VALUES ('$idPedido', '$producto', $cantidad, '$nota', $precioUnitario, 'pendiente')";
        
        return $this->conn->query($sql);
    }
}
