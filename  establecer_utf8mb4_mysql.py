import pymysql

# Configuración de la conexión a la base de datos
connection = pymysql.connect(
    host='host',
    user='usuario',
    password='password',
    database='basedatos',
    charset='utf8mb4'
)

# Lista de reemplazos de caracteres erróneos y sus correcciones
replacements = [
    ('Ã±', 'ñ'), ('Ã¡', 'á'), ('Ã©', 'é'), ('Ã­', 'í'), ('Ã³', 'ó'), ('Ãº', 'ú'),
    ('Ã', 'Á'), ('Ã‰', 'É'), ('Ã', 'Í'), ('Ã“', 'Ó'), ('Ãš', 'Ú'), ('Ã‘', 'Ñ'),
    ('Ã¼', 'ü'), ('Ã§', 'ç'), ('Â¿', '¿'), ('Â¡', '¡'), ('Ã…Â½', 'é'),
    ('Ã¢â‚¬¡', 'á'), ('Ã¢â‚¬â€œ', 'ñ'), ('Ã…¡', 'Á'), ('Ãƒ¡', 'á'),
    ('ÃƒÂ©', 'é'), ('ÃƒÂ±', 'ñ'), ('ÃƒÂ³', 'ó'), ('ÃƒÂ­', 'í'), ('ÃƒÂº', 'ú'),
    ('Ãƒâ€˜', 'Ñ')
]

try:
    with connection.cursor() as cursor:
        # Obtener todas las tablas y columnas de tipo texto
        cursor.execute("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND data_type IN ('varchar', 'text', 'char');
        """)
        
        tables_columns = cursor.fetchall()

        # Iterar sobre cada tabla y columna
        for table_name, column_name in tables_columns:
            # Escapar nombres de tablas y columnas con comillas invertidas
            escaped_table_name = f"`{table_name}`"
            escaped_column_name = f"`{column_name}`"
            
            # Construir el cuerpo de los reemplazos en la consulta
            replace_expression = escaped_column_name
            for old_value, new_value in replacements:
                replace_expression = f"REPLACE({replace_expression}, '{old_value}', '{new_value}')"
            
            # Construir la consulta final de actualización con WHERE
            final_query = f"""
                UPDATE {escaped_table_name} 
                SET {escaped_column_name} = {replace_expression}
                WHERE {escaped_column_name} REGEXP 'Ã±|Ã¡|Ã©|Ã­|Ã³|Ãº|Ã|Ã‰|Ã|Ã“|Ãš|Ã‘|Ã¼|Ã§|Â¿|Â¡|Ã…Â½|Ã¢â‚¬¡|Ã¢â‚¬â€œ|Ã…¡|Ãƒ¡|ÃƒÂ©|ÃƒÂ±|ÃƒÂ³|ÃƒÂº|ÃƒÂ­';
            """
            
            # Ejecutar la consulta de actualización
            print(f"Ejecutando: {final_query}")
            cursor.execute(final_query)
            connection.commit()

except Exception as e:
    print(f"Error: {e}")
finally:
    connection.close()