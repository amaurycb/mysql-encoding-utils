import mysql.connector

def change_table_encoding_and_collation(database_name, user, password, host='localhost', port=3306):
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_name
        )
        cursor = connection.cursor()

        # Obtener todas las tablas del esquema
        cursor.execute(f"SHOW TABLES FROM {database_name};")
        tables = cursor.fetchall()

        # Iterar sobre cada tabla y cambiar la codificación y collation
        for table in tables:
            table_name = table[0]
            alter_query = f"ALTER TABLE {table_name} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            print(f"Ejecutando: {alter_query}")
            cursor.execute(alter_query)
            connection.commit()

        print(f"Se ha cambiado la codificación y collation de todas las tablas en la base de datos '{database_name}'.")

    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    # Parámetros de conexión a la base de datos
    db_name = 'nombre_de_la_base_de_datos'
    db_user = 'usuario'
    db_password = 'password'
    db_host = 'localhost'  
    db_port = 3306  # Cambia el puerto si es necesario

    change_table_encoding_and_collation(db_name, db_user, db_password, db_host, db_port)
