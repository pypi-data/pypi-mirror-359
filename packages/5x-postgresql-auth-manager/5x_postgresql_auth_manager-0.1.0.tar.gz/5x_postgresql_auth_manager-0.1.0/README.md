# 5x-postgresql-auth-manager

A Python package to manage PostgreSQL connections using environment variables.

## Installation

```bash
pip install 5x-postgresql-auth-manager
```

## Usage

This package simplifies connecting to PostgreSQL by reading connection details from environment variables. It provides a `PostgreSQLConnectionManager` class that handles connection establishment and management.

### Environment Variables

Set the following environment variables with your PostgreSQL connection details:

- `FIVEX_POSTGRESQL_HOST`: The hostname or IP address of your PostgreSQL server.
- `FIVEX_POSTGRESQL_PORT`: The port number of your PostgreSQL server (defaults to `5432`).
- `FIVEX_POSTGRESQL_DATABASE`: The name of the database to connect to.
- `FIVEX_POSTGRESQL_USER`: The username for connecting to the database.
- `FIVEX_POSTGRESQL_PASSWORD`: The password for the specified user.

### Example

```python
import os
from postgresql_auth.postgresql_auth import PostgreSQLConnectionManager

# Set environment variables (replace with your actual credentials)
os.environ['FIVEX_POSTGRESQL_HOST'] = 'localhost'
os.environ['FIVEX_POSTGRESQL_PORT'] = '5432'
os.environ['FIVEX_POSTGRESQL_DATABASE'] = 'mydatabase'
os.environ['FIVEX_POSTGRESQL_USER'] = 'myuser'
os.environ['FIVEX_POSTGRESQL_PASSWORD'] = 'mypassword'

try:
    manager = PostgreSQLConnectionManager()
    with manager.get_connection() as conn:
        print("Successfully connected to PostgreSQL!")
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"PostgreSQL Version: {version[0]}")

except ValueError as e:
    print(f"Configuration Error: {e}")
except ConnectionError as e:
    print(f"Connection Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```
