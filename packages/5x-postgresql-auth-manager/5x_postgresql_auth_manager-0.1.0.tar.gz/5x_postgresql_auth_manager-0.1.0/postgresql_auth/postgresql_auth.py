import os
from typing import Dict
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection

class PostgreSQLConnectionManager:
    """
    Manages PostgreSQL connections using environment variables.
    Required environment variables:
    - FIVEX_POSTGRESQL_HOST: PostgreSQL host
    - FIVEX_POSTGRESQL_PORT: PostgreSQL port (defaults to 5432)
    - FIVEX_POSTGRESQL_DATABASE: Database name
    - FIVEX_POSTGRESQL_USER: Database username
    - FIVEX_POSTGRESQL_PASSWORD: Database password
    """
    
    def __init__(self):
        """Initialize the PostgreSQL connection manager using environment variables."""
        self._connection = None
        self._validate_and_set_credentials()
    
    def _validate_and_set_credentials(self) -> None:
        """
        Validate and set PostgreSQL credentials from environment variables.
        
        Raises:
            ValueError: If required environment variables are missing
            ValueError: If credentials are empty or malformed
        """
        # Get credentials from environment
        host = os.getenv('FIVEX_POSTGRESQL_HOST')
        port = os.getenv('FIVEX_POSTGRESQL_PORT', '5432')
        database = os.getenv('FIVEX_POSTGRESQL_DATABASE')
        user = os.getenv('FIVEX_POSTGRESQL_USER')
        password = os.getenv('FIVEX_POSTGRESQL_PASSWORD')

        # Check for missing credentials
        missing_vars = []
        if not host:
            missing_vars.append('FIVEX_POSTGRESQL_HOST')
        if not database:
            missing_vars.append('FIVEX_POSTGRESQL_DATABASE')
        if not user:
            missing_vars.append('FIVEX_POSTGRESQL_USER')
        if not password:
            missing_vars.append('FIVEX_POSTGRESQL_PASSWORD')
            
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Validate credential format
        if not host.strip():
            raise ValueError("PostgreSQL host is invalid or empty")
        if not database.strip():
            raise ValueError("PostgreSQL database name is invalid or empty")
        if not user.strip():
            raise ValueError("PostgreSQL username is invalid or empty")
        if not password.strip():
            raise ValueError("PostgreSQL password is invalid or empty")

        # Validate port
        try:
            port_int = int(port)
            if port_int < 1 or port_int > 65535:
                raise ValueError("PostgreSQL port must be between 1 and 65535")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("PostgreSQL port must be a valid integer")
            raise

        self.credentials = {
            'host': host,
            'port': port_int,
            'database': database,
            'user': user,
            'password': password
        }

    def get_connection(self) -> connection:
        """
        Get or create a PostgreSQL connection instance.
        
        Returns:
            psycopg2.connection: Configured PostgreSQL connection
            
        Raises:
            psycopg2.OperationalError: If connection fails due to invalid credentials or network issues
            psycopg2.DatabaseError: If database-specific errors occur
            ConnectionError: If connection to PostgreSQL fails
            Exception: For other unexpected errors
        """
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(**self.credentials)
                # Test the connection immediately
                with self._connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    
            except psycopg2.OperationalError as e:
                error_msg = str(e).lower()
                if "password authentication failed" in error_msg:
                    raise ValueError("Invalid PostgreSQL username or password") from e
                elif "could not connect to server" in error_msg or "timeout" in error_msg:
                    raise ConnectionError("Could not connect to PostgreSQL server. Check host and port.") from e
                elif "database" in error_msg and "does not exist" in error_msg:
                    raise ValueError("PostgreSQL database does not exist") from e
                else:
                    raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}") from e
            except psycopg2.DatabaseError as e:
                raise ValueError(f"PostgreSQL database error: {str(e)}") from e
            except Exception as e:
                raise ConnectionError(f"Unexpected error connecting to PostgreSQL: {str(e)}") from e
                
        return self._connection

    def get_cursor(self):
        """
        Get a cursor from the connection.
        
        Returns:
            psycopg2.cursor: Database cursor for executing queries
        """
        connection = self.get_connection()
        return connection.cursor()

    def close_connection(self):
        """
        Close the connection if it exists.
        """
        if self._connection and not self._connection.closed:
            self._connection.close()

    def __enter__(self):
        """
        Context manager entry.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - close connection.
        """
        self.close_connection()

# Example usage
if __name__ == "__main__":
    try:
        # Create manager and get connection
        manager = PostgreSQLConnectionManager()
        connection = manager.get_connection()
        print("Successfully connected to PostgreSQL")
        
        # Test with a simple query
        with manager.get_cursor() as cursor:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            print(f"PostgreSQL version: {result[0]}")
            
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
