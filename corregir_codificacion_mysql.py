import pymysql
import concurrent.futures
import sqlparse

# Configuración de la conexión a la base de datos
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'db',
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
num_threads = 3  # Puedes cambiar este valor para controlar la cantidad de hilos

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
                SET {column} = 
                replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace({column},'Ã±','ñ'),'Ã¡','á'),'Ã©','é'),'Ã­','í'),'Ã³','ó'),'Ãº','ú'),'Ã','Á'),'Ã‰','É'),'Ã','Í'),'Ã“','Ó'),'Ãš','Ú'),'Ã‘','Ñ'),'Ã¼','ü'),'Ã§','ç'),'Â¿','¿'),'Â¡','¡'),'Ã…Â½','é'),'Ã¢â‚¬¡','á'),'Ã¢â‚¬â€œ','ñ'),'Ã…¡','Á'),'Ãƒ¡','á'),'ÃƒÂ©','é'),'ÃƒÂ±','ñ'),'ÃƒÂ³','ó'),'ÃƒÂ­','í'),'ÃƒÂº','ú'),'Ãƒâ€˜','Ñ')
                WHERE regexp_like({column}, 'Ã±|Ã¡|Ã©|Ã­|Ã³|Ãº|Ã|Ã‰|Ã|Ã“|Ãš|Ã‘|Ã¼|Ã§|Â¿|Â¡|Ã…Â½|Ã¢â‚¬¡|Ã¢â‚¬â€œ|Ã…¡|Ãƒ¡|ÃƒÂ©|ÃƒÂ±|ÃƒÂ³|ÃƒÂº|ÃƒÂ­');
            """.format(table=escaped_table_name, column=escaped_column_name)
            formatted_query = sqlparse.format(final_query, reindent=True, keyword_case='upper')

            
            # Ejecutar la consulta de actualización
            print(formatted_query)
            cursor.execute(final_query)
            connection.commit()
    except Exception as e:
        print("Error en {}.{}: {}".format(table_name, column_name, e))
    finally:
        connection.close()


def main(db_config, num_threads, table_names=None, exclude_tables=None):
    if table_names and exclude_tables:
        raise ValueError("No puedes especificar table_names y exclude_tables al mismo tiempo.")
    
    try:
        # Crear una conexión principal para obtener las tablas y columnas
        connection = pymysql.connect(**db_config)
                
        with connection.cursor() as cursor:
            if table_names:
                # Construir una cláusula WHERE para filtrar las tablas
                table_names_str = ', '.join(['"{}"'.format(name) for name in table_names])
                query = """
                    SELECT table_name, column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = DATABASE() 
                    AND data_type IN ('varchar', 'text', 'char', 'mediumtext')
                    AND table_name IN ({})
                """.format(table_names_str)
            elif exclude_tables:
                # Construir una cláusula WHERE para excluir las tablas
                exclude_tables_str = ', '.join(['"{}"'.format(name) for name in exclude_tables])
                query = """
                    SELECT table_name, column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = DATABASE() 
                    AND data_type IN ('varchar', 'text', 'char', 'mediumtext')
                    AND table_name NOT IN ({})
                """.format(exclude_tables_str)    
            else:
                # Obtener todas las tablas y columnas de tipo texto
                query = """
                    SELECT table_name, column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = DATABASE() 
                    AND data_type IN ('varchar', 'text', 'char', 'mediumtext');
                """
            cursor.execute(query)
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
    # Lista de tablas a procesar (o dejar vacío para procesar todas)
    tablas_a_procesar = []

    # Lista de tablas a excluir (o dejar vacío para no excluir ninguna)
    tablas_a_excluir = ["tabla1", "tabla2"] 
      
    # Ejecutar el script con la configuración de la base de datos, 
    # el número de hilos y la lista de tablas
    main(db_config, num_threads, tablas_a_procesar)
