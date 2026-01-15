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

// 1. AUTO-MIGRATION: Check if 'estado' column exists, if not add it
$checkColumn = $conn->query("SHOW COLUMNS FROM pedidos LIKE 'estado'");
if ($checkColumn->num_rows == 0) {
    $conn->query("ALTER TABLE pedidos ADD COLUMN estado VARCHAR(50) DEFAULT 'pendiente'");
}

// 2. HANLDE REQUESTS
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    // Fetch all orders
    $sql = "SELECT * FROM pedidos ORDER BY id DESC"; // Assuming 'id' is auto-increment primary key, or use whatever timestamp column exists
    // If no distinct primary key for ordering, maybe just SELECT *
    // Check if table has an ID or timestamp. From previous view, it has id_pedido, producto, cantidad, nota. 
    // Usually tables have an auto-inc ID. Let's just do SELECT * and we can refine order later.
    $sql = "SELECT * FROM pedidos";
    $result = $conn->query($sql);

    $pedidos = [];
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $pedidos[] = $row;
        }
    }
    echo json_encode($pedidos);

} elseif ($method === 'POST') {
    // Update status
    $data = json_decode(file_get_contents("php://input"), true);
    
    if (isset($data['id_pedido']) && isset($data['estado']) && isset($data['producto'])) {
        // We need to identify the row. 
        // NOTE: 'id_pedido' in the python script is a Ticket ID (UUID group), not a unique row ID.
        // A single ticket ID has multiple rows (products).
        // If we want to update the status of a specific ITEM in the ticket, we need a unique row identifier.
        // Let's check the schema again or assume we update by (id_pedido, producto).
        // Best approach: Update based on id_pedido AND producto if we treat them as individual items on the board.
        // OR if the board shows whole tickets. The user said "show orders received... manage (change status)".
        // Usually, individual items might be completed separately in a kitchen (e.g. drink ready, pizza baking).
        // Let's assume we update by `id_pedido` AND `producto` just to be safe, or just `id_pedido` if updating the whole ticket.
        // Let's try to find a unique ID. If not, we use the combo.
        
        // For now, I'll allow updating by ticket ID + Product to be specific, or just Ticket ID.
        // Let's update the specific item for now.
        $id_pedido = $conn->real_escape_string($data['id_pedido']);
        $estado = $conn->real_escape_string($data['estado']);
        $producto = $conn->real_escape_string($data['producto']); // Using product name as secondary key if needed

        $sql = "UPDATE pedidos SET estado='$estado' WHERE id_pedido='$id_pedido' AND producto='$producto'";
        
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
