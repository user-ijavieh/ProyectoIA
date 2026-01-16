<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "restaurante_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// 1. Add id_pedido if not exists
$checkId = $conn->query("SHOW COLUMNS FROM pedidos LIKE 'id_pedido'");
if ($checkId->num_rows == 0) {
    $sql = "ALTER TABLE pedidos ADD COLUMN id_pedido VARCHAR(50) NOT NULL AFTER id";
    if ($conn->query($sql) === TRUE) {
        echo "Column 'id_pedido' added successfully.<br>";
    } else {
        echo "Error adding 'id_pedido': " . $conn->error . "<br>";
    }
} else {
    echo "Column 'id_pedido' already exists.<br>";
}

// 2. Modify estado to VARCHAR(50)
// We assume if it exists, we force it to VARCHAR to support our app's logic
$sql = "ALTER TABLE pedidos MODIFY COLUMN estado VARCHAR(50) DEFAULT 'pendiente'";
if ($conn->query($sql) === TRUE) {
    echo "Column 'estado' modified to VARCHAR(50) successfully.<br>";
} else {
    echo "Error modifying 'estado': " . $conn->error . "<br>";
}

$conn->close();
?>
