import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="restaurante_db"
        )
        return connection
    except Error as e:
        print(f"Error al conectar: {e}")
        return None

def guardar_pedido(id_pedido, producto, cantidad, nota):
    """Inserta un producto individual asociado a un ID de ticket único."""
    conexion = get_db_connection()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor()
            sql = "INSERT INTO pedidos (id_pedido, producto, cantidad, nota) VALUES (%s, %s, %s, %s)"
            valores = (id_pedido, producto, cantidad, nota)
            cursor.execute(sql, valores)
            conexion.commit()
            return True
        except Error as e:
            print(f"Error insertando pedido: {e}")
            return False
        finally:
            conexion.close()
    return False

def obtener_estado_pedido(id_pedido):
    """Devuelve el estado y los detalles de un pedido dado su ID."""
    conexion = get_db_connection()
    if conexion and conexion.is_connected():
        try:
            cursor = conexion.cursor(dictionary=True)
            # Buscamos cualquier item con ese ticket_id para ver el estado general
            # Asumimos que todos los items del mismo pedido cambian de estado juntos (por el update agrupado)
            sql = "SELECT estado, producto, cantidad FROM pedidos WHERE id_pedido = %s"
            cursor.execute(sql, (id_pedido,))
            resultados = cursor.fetchall()
            
            if resultados:
                # Retornamos el estado del primer item (deberían ser iguales) y la lista de items
                estado_general = resultados[0]['estado']
                items = [{"producto": r['producto'], "cantidad": r['cantidad']} for r in resultados]
                return {"estado": estado_general, "items": items}
            return None
        except Error as e:
            print(f"Error consultando pedido: {e}")
            return None
        finally:
            conexion.close()
    return None