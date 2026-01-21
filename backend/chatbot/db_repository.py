import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"), 
            user=os.getenv("DB_USER", "root"), 
            password=os.getenv("DB_PASSWORD", ""), 
            database=os.getenv("DB_NAME", "restaurante_db")
        )
    except Error as e: 
        print(f"Error de conexión: {e}")
        return None

def obtener_menu_db():
    """Obtiene la lista de productos disponibles desde la tabla menu."""
    conexion = get_db_connection()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre_producto FROM menu WHERE disponible = 1")
            # Convertimos a minúsculas para un mejor matching con la IA
            return [row[0].lower() for row in cursor.fetchall()]
        finally: 
            conexion.close()
    return []

def obtener_precio_producto(nombre):
    """Busca el precio de un producto específico en la tabla menu."""
    conexion = get_db_connection()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT precio FROM menu WHERE nombre_producto = %s", (nombre.lower(),))
            res = cursor.fetchone()
            return float(res[0]) if res else 0.0
        finally: 
            conexion.close()
    return 0.0

def guardar_pedido(id_pedido, producto, cantidad, nota, precio_unitario):
    """Guarda el pedido incluyendo el precio unitario."""
    conexion = get_db_connection()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            # SQL actualizada para incluir precio_unitario
            sql = "INSERT INTO pedidos (id_pedido, producto, cantidad, nota, precio_unitario) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (id_pedido, producto, cantidad, nota, precio_unitario))
            conexion.commit()
            return True
        finally: 
            conexion.close()
    return False

def obtener_estado_pedido(id_pedido):
    """Consulta el estado de un ticket."""
    conexion = get_db_connection()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT estado, producto, cantidad FROM pedidos WHERE id_pedido = %s"
            cursor.execute(sql, (id_pedido,))
            resultados = cursor.fetchall()
            if resultados:
                return {"estado": resultados[0]['estado'], "items": resultados}
            return None
        finally: 
            conexion.close()
    return None