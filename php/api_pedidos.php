<?php
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST");

$conn = new mysqli("localhost", "root", "", "restaurante_db");

if ($conn->connect_error) die(json_encode(["error" => $conn->connect_error]));

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $mode = isset($_GET['mode']) ? $_GET['mode'] : 'tablero';
    $sql = ($mode === 'historial') ? "SELECT * FROM pedidos WHERE estado = 'archivado' ORDER BY fecha DESC" 
                                   : "SELECT * FROM pedidos WHERE estado != 'archivado' ORDER BY id DESC";
    $result = $conn->query($sql);
    $pedidos = [];
    while($row = $result->fetch_assoc()) $pedidos[] = $row;
    echo json_encode($pedidos);

} elseif ($method === 'POST') {
    $data = json_decode(file_get_contents("php://input"), true);
    if (isset($data['id_pedido'], $data['estado'])) {
        $id = $conn->real_escape_string($data['id_pedido']);
        $est = $conn->real_escape_string($data['estado']);
        $prod = isset($data['producto']) ? $conn->real_escape_string($data['producto']) : 'ALL';
        $sql = ($prod === 'ALL') ? "UPDATE pedidos SET estado='$est', fecha=NOW() WHERE id_pedido='$id'" 
                                 : "UPDATE pedidos SET estado='$est', fecha=NOW() WHERE id_pedido='$id' AND producto='$prod'";
        $conn->query($sql);
        echo json_encode(["message" => "OK"]);
    }
}
$conn->close();
?>