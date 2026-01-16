<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "restaurante_db";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
echo "Connected successfully\n";

$sql = "DESCRIBE pedidos";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
  while($row = $result->fetch_assoc()) {
    echo "Field: " . $row["Field"]. " - Type: " . $row["Type"]. "\n";
  }
} else {
  echo "0 results";
}
$conn->close();
?>
