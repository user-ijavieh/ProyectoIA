<?php
/**
 * Controlador de endpoints HTTP para pedidos
 */

require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/pedidos.service.php';
require_once __DIR__ . '/pedidos.repository.php';

// Configurar headers
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

// Manejar preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Inicializar servicios
$conn = getDbConnection();
$repository = new PedidosRepository($conn);
$service = new PedidosService($repository);

// Obtener método HTTP
$method = $_SERVER['REQUEST_METHOD'];

try {
    switch ($method) {
        case 'GET':
            handleGet($service);
            break;
            
        case 'POST':
            handlePost($service);
            break;
            
        case 'PUT':
            handlePut($service);
            break;
            
        default:
            http_response_code(405);
            echo json_encode([
                'error' => 'Método no permitido',
                'allowed_methods' => ['GET', 'POST', 'PUT']
            ]);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Error del servidor',
        'message' => $e->getMessage()
    ]);
} finally {
    $conn->close();
}

/**
 * Maneja peticiones GET
 */
function handleGet($service) {
    $mode = isset($_GET['mode']) ? $_GET['mode'] : 'tablero';
    
    if (isset($_GET['stats'])) {
        // Endpoint de estadísticas
        $stats = $service->obtenerEstadisticas();
        echo json_encode($stats);
        return;
    }
    
    // Endpoint de listado de pedidos
    $pedidos = $service->obtenerPedidos($mode);
    echo json_encode($pedidos);
}

/**
 * Maneja peticiones POST - Actualización de estado o creación
 */
function handlePost($service) {
    $data = json_decode(file_get_contents("php://input"), true);
    
    if (!$data) {
        http_response_code(400);
        echo json_encode(['error' => 'Datos inválidos']);
        return;
    }
    
    // Determinar si es actualización o creación
    if (isset($data['id_pedido']) && isset($data['estado'])) {
        // Actualización de estado
        $producto = isset($data['producto']) ? $data['producto'] : 'ALL';
        $resultado = $service->actualizarEstado(
            $data['id_pedido'],
            $data['estado'],
            $producto
        );
        
        if ($resultado['success']) {
            echo json_encode(['message' => 'OK', 'data' => $resultado]);
        } else {
            http_response_code(400);
            echo json_encode(['error' => $resultado['message']]);
        }
    } elseif (isset($data['id_pedido']) && isset($data['producto']) && isset($data['cantidad'])) {
        // Creación de nuevo pedido
        $resultado = $service->crearNuevoPedido($data);
        
        if ($resultado['success']) {
            http_response_code(201);
            echo json_encode(['message' => 'Creado', 'data' => $resultado]);
        } else {
            http_response_code(400);
            echo json_encode(['error' => $resultado['message']]);
        }
    } else {
        http_response_code(400);
        echo json_encode(['error' => 'Datos incompletos']);
    }
}

/**
 * Maneja peticiones PUT - Actualización completa
 */
function handlePut($service) {
    $data = json_decode(file_get_contents("php://input"), true);
    
    if (!$data || !isset($data['id_pedido']) || !isset($data['estado'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Datos incompletos']);
        return;
    }
    
    $resultado = $service->actualizarEstado(
        $data['id_pedido'],
        $data['estado'],
        'ALL'
    );
    
    if ($resultado['success']) {
        echo json_encode(['message' => 'OK', 'data' => $resultado]);
    } else {
        http_response_code(400);
        echo json_encode(['error' => $resultado['message']]);
    }
}
