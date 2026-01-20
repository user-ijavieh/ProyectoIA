<?php
/**
 * Configuración de la base de datos
 */

define('DB_HOST', getenv('DB_HOST') ?: 'localhost');
define('DB_USER', getenv('DB_USER') ?: 'root');
define('DB_PASS', getenv('DB_PASSWORD') ?: '');
define('DB_NAME', getenv('DB_NAME') ?: 'restaurante_db');

/**
 * Obtener conexión a la base de datos
 */
function getDbConnection() {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    
    if ($conn->connect_error) {
        die(json_encode(["error" => "Error de conexión: " . $conn->connect_error]));
    }
    
    return $conn;
}
