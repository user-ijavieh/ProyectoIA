import mysql.connector
from mysql.connector import Error

def guardar_pedido(id_pedido, producto, cantidad, nota):
    """Inserta un producto individual asociado a un ID de ticket único."""
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",      # Usuario por defecto de XAMPP
            password="",      # Contraseña por defecto de XAMPP
            database="restaurante_db"
        )
        
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "INSERT INTO pedidos (id_pedido, producto, cantidad, nota) VALUES (%s, %s, %s, %s)"
            valores = (id_pedido, producto, cantidad, nota)
            
            cursor.execute(sql, valores)
            conexion.commit()
            return True
            
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return False
    finally:
        if conexion and conexion.is_connected():
            conexion.close()