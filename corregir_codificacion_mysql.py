import pymysql
import concurrent.futures

# Configuración de la conexión a la base de datos
db_config = {
    'host': 'host',
    'user': 'usuario',
    'password': 'password',
    'database': 'basedatos',
    'charset': 'utf8mb4'
}

# Lista de reemplazos de caracteres erróneos y sus correcciones
replacements = [
    ('Ã±', 'ñ'), ('Ã¡', 'á'), ('Ã©', 'é'), ('Ã­', 'í'), ('Ã³', 'ó'), ('Ãº', 'ú'),
    ('Ã', 'Á'), ('Ã‰', 'É'), ('Ã', 'Í'), ('Ã“', 'Ó'), ('Ãš', 'Ú'), ('Ã‘', 'Ñ'),
    ('Ã¼', 'ü'), ('Ã§', 'ç'), ('Â¿', '¿'), ('Â¡', '¡'), ('Ã…Â½', 'é'),
    ('Ã¢â‚¬¡', 'á'), ('Ã¢â‚¬â€œ', 'ñ'), ('Ã…¡', 'Á'), ('Ãƒ¡', 'á'),
    ('ÃƒÂ©', 'é'), ('ÃƒÂ±', 'ñ'), ('ÃƒÂ³', 'ó'), ('ÃƒÂ­', 'í'), ('ÃƒÂº', 'ú'),
    ('Ãƒâ€˜', 'Ñ')
]

# Variable para controlar la cantidad de hilos
num_threads = 5  # Puedes cambiar este valor para controlar la cantidad de hilos

def procesar_columna(table_name, column_name, db_config):
    # Crear una nueva conexión dentro del hilo
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # Escapar nombres de tablas y columnas con comillas invertidas
            escaped_table_name = "`{}`".format(table_name)
            escaped_column_name = "`{}`".format(column_name)
            
            # Construir el cuerpo de los reemplazos en la consulta
            replace_expression = escaped_column_name
            for old_value, new_value in replacements:
                replace_expression = "REPLACE({}, '{}', '{}')".format(replace_expression, old_value, new_value)
            
            # Construir la consulta final de actualización con WHERE
            final_query = """
                UPDATE {table} 
                SET {column} = {replace_expr}
                WHERE {column} REGEXP 'Ã±|Ã¡|Ã©|Ã­|Ã³|Ãº|Ã|Ã‰|Ã|Ã“|Ãš|Ã‘|Ã¼|Ã§|Â¿|Â¡|Ã…Â½|Ã¢â‚¬¡|Ã¢â‚¬â€œ|Ã…¡|Ãƒ¡|ÃƒÂ©|ÃƒÂ±|ÃƒÂ³|ÃƒÂº|ÃƒÂ­';
            """.format(table=escaped_table_name, column=escaped_column_name, replace_expr=replace_expression)
            
            # Ejecutar la consulta de actualización
            print("Ejecutando: {}".format(final_query))
            cursor.execute(final_query)
            connection.commit()
    except Exception as e:
        print("Error en {}.{}: {}".format(table_name, column_name, e))
    finally:
        connection.close()


def main(db_config, num_threads):
    try:
        # Crear una conexión principal para obtener las tablas y columnas
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # Obtener todas las tablas y columnas de tipo texto
            cursor.execute("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND data_type IN ('varchar', 'text', 'char');
            """)
            
            tables_columns = cursor.fetchall()
        
        # Ejecutar concurrentemente utilizando hilos
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Ejecutar cada columna en un hilo separado
            futures = [executor.submit(procesar_columna, table_name, column_name, db_config) for table_name, column_name in tables_columns]

            # Aguardar a que todos los hilos finalicen
            for future in concurrent.futures.as_completed(futures):
                future.result()

    except Exception as e:
        print("Error: {}".format(e))
    finally:
        connection.close()


if __name__ == "__main__":
    # Ejecutar el script con la configuración de la base de datos y el número de hilos
    main(db_config, num_threads)