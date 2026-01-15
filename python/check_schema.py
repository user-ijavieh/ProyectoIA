import mysql.connector
from mysql.connector import Error

def check_schema():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="restaurante_db"
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("DESCRIBE pedidos")
            columns = cursor.fetchall()
            print("Columns in 'pedidos' table:")
            for col in columns:
                print(col)
            conexion.close()
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
