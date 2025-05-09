# SQLite Database Driver Implementation
import sqlite3
import pandas as pd
from src.core.database.connection import BaseConnection, ConnectionError

class SQLiteConnection(BaseConnection):
    """Concrete implementation for SQLite database connections."""

    def connect(self):
        """Establish a connection to the SQLite database."""
        if not self.connection_params or "database_path" not in self.connection_params:
            raise ConnectionError("SQLite connection parameters must include 'database_path'.")
        
        db_path = self.connection_params["database_path"]
        try:
            self.connection = sqlite3.connect(db_path)
            # print(f"Successfully connected to SQLite database: {db_path}") # For debugging
        except sqlite3.Error as e:
            raise ConnectionError(f"Error connecting to SQLite database at {db_path}: {e}")

    def disconnect(self):
        """Close the SQLite database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            # print("Disconnected from SQLite database.") # For debugging

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a pandas DataFrame."""
        if not self.connection:
            raise ConnectionError("Not connected to any database. Call connect() first.")
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except pd.io.sql.DatabaseError as e:
            # This can happen if the query is invalid or table doesn't exist
            raise ConnectionError(f"Error executing query: {e}. Query: '{query}'")
        except Exception as e:
            raise ConnectionError(f"An unexpected error occurred during query execution: {e}")

    def test_connection(self) -> bool:
        """Test if the connection is alive by executing a simple query."""
        if not self.connection:
            return False
        try:
            # A simple query to test the connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except sqlite3.Error:
            return False

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy database for testing
    db_file = "/home/ubuntu/overwatch_command_center/data/test_sqlite.db"
    conn_params = {"database_path": db_file}
    
    # Ensure data directory exists
    import os
    os.makedirs(os.path.dirname(db_file), exist_ok=True)

    try:
        with SQLiteConnection(conn_params) as db:
            print(f"Testing connection to {db_file}...")
            if db.test_connection():
                print("Connection successful!")
                
                # Create a test table and insert data
                db.connection.execute("DROP TABLE IF EXISTS test_table")
                db.connection.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")
                db.connection.execute("INSERT INTO test_table VALUES (1, 'Alice'), (2, 'Bob')")
                db.connection.commit()
                print("Test table created and data inserted.")

                # Execute a query
                df_results = db.execute_query("SELECT * FROM test_table")
                print("Query results:")
                print(df_results)
            else:
                print("Connection failed.")

    except ConnectionError as e:
        print(f"Database operation failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up the dummy database if it was created
        # if os.path.exists(db_file):
        #     os.remove(db_file)
        #     print(f"Cleaned up {db_file}")
        pass

