<?php
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST");

$servername = "localhost";
$username = "root";
$password = "";
$dbname = "restaurante_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}

// 1. AUTO-MIGRATION
$checkColumn = $conn->query("SHOW COLUMNS FROM pedidos LIKE 'estado'");
if ($checkColumn->num_rows == 0) {
    $conn->query("ALTER TABLE pedidos ADD COLUMN estado VARCHAR(50) DEFAULT 'pendiente'");
}

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $mode = isset($_GET['mode']) ? $_GET['mode'] : 'tablero';

    if ($mode === 'historial') {
        $sql = "SELECT * FROM pedidos WHERE estado = 'archivado' ORDER BY fecha DESC";
    } else {
        // Tablero: todo menos archivado
        $sql = "SELECT * FROM pedidos WHERE estado != 'archivado' ORDER BY id DESC";
    }
    
    $result = $conn->query($sql);

    $pedidos = [];
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $pedidos[] = $row;
        }
    }
    echo json_encode($pedidos);

} elseif ($method === 'POST') {
    $data = json_decode(file_get_contents("php://input"), true);
    
    if (isset($data['id_pedido']) && isset($data['estado'])) {
        $id_pedido = $conn->real_escape_string($data['id_pedido']);
        $estado = $conn->real_escape_string($data['estado']);
        $producto = isset($data['producto']) ? $conn->real_escape_string($data['producto']) : 'ALL';

        // Lógica de actualización agrupada
        if ($producto === 'ALL') {
            $sql = "UPDATE pedidos SET estado='$estado', fecha=NOW() WHERE id_pedido='$id_pedido'";
        } else {
            $sql = "UPDATE pedidos SET estado='$estado', fecha=NOW() WHERE id_pedido='$id_pedido' AND producto='$producto'";
        }
        
        if ($conn->query($sql) === TRUE) {
            echo json_encode(["message" => "Estado actualizado correctamente"]);
        } else {
            echo json_encode(["error" => "Error updating record: " . $conn->error]);
        }
    } else {
        echo json_encode(["error" => "Missing parameters"]);
    }
}

$conn->close();
?>
