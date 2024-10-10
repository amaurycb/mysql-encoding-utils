
# MySQL Encoding Utils

This repository contains two useful scripts for managing character encoding in MySQL databases, focusing on fixing encoding issues caused by data migrations. It is common that during a migration, incorrect conversions between character encodings occur, or the source system does not properly handle Latin-1 encoding. To solve these problems, you can follow the following strategies:

1. Ensure that the database and tables are using the `utf8mb4` encoding.
2. Clean the existing data, correcting instances of incorrect characters, such as the letter "Ñ" or other special characters.

## Scripts

1. `establecer_utf8mb4_mysql.py`: Changes the encoding of all tables in a MySQL database to `utf8mb4` and the collation to `utf8mb4_unicode_ci`.
2. `corregir_codificacion_mysql.py`: Corrects incorrect characters in text columns caused by encoding issues during data migration.

## Requirements

- Python 3.6
- Libraries: `mysql-connector-python`, `PyMySQL`

To install the dependencies, run:

```bash
pip install mysql-connector-python PyMySQL
```

## Usage

### 1. Change the encoding of the tables (`establecer_utf8mb4_mysql.py`)

This script converts the encoding of all tables in a database to `utf8mb4` to avoid future compatibility issues with special characters.

#### Command

```bash
python establecer_utf8mb4_mysql.py
```

### 2. Fix incorrect characters (`corregir_codificacion_mysql.py`)

This script finds and replaces incorrectly encoded characters that were damaged during the data migration. For example, it fixes characters like "Ã±" which should be "ñ".

#### Command

```bash
python corregir_codificacion_mysql.py
```

## Recommended steps before running the scripts

1. **Make a backup**: Due to the significant changes these scripts will apply to the database, it is essential to perform a full backup before running them. This is especially important when cleaning or migrating data.

   You can use the following command to create the backup:

   ```bash
   mysqldump -u user -p database_name > backup.sql
   ```

2. **Verify the current encoding**: Before running the scripts, ensure that the database use `utf8mb4`. This will help prevent additional encoding issues.

3. **Correctly configure connection parameters**: Edit the scripts with the correct connection credentials and parameters for your environment before running them.

## Warning

These scripts apply irreversible changes to the database. It is recommended to test them in a development or staging environment before deploying them in production. **I am not responsible for any data loss, malfunction, or errors that may occur when using these scripts.**

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
