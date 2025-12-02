"""
SQL Server Connection Manager
Handles connections to Microsoft SQL Server databases
"""
import pyodbc
import pandas as pd
from typing import Optional, Dict, Any, List
import sys
import os

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import SQL_SERVER_CONFIG


class SQLServerConnector:
    """MS SQL Server connection manager"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize SQL Server connector.
        
        Args:
            config: Optional configuration dictionary. Uses SQL_SERVER_CONFIG if not provided.
        """
        self.config = config or SQL_SERVER_CONFIG
        self.connection = None
    
    def connect(self) -> bool:
        """
        Establish connection to SQL Server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.config["trusted_connection"].lower() == "yes":
                conn_str = (
                    f"DRIVER={self.config['driver']};"
                    f"SERVER={self.config['server']};"
                    f"DATABASE={self.config['database']};"
                    "Trusted_Connection=yes;"
                )
            else:
                conn_str = (
                    f"DRIVER={self.config['driver']};"
                    f"SERVER={self.config['server']};"
                    f"DATABASE={self.config['database']};"
                    f"UID={self.config['username']};"
                    f"PWD={self.config['password']};"
                )
            
            self.connection = pyodbc.connect(conn_str)
            print(f"✅ Connected to SQL Server: {self.config['server']}/{self.config['database']}")
            return True
        except Exception as e:
            print(f"❌ SQL Server connection error: {e}")
            return False
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            pandas DataFrame with query results
            
        Raises:
            Exception: If not connected or query fails
        """
        if not self.connection:
            raise Exception("Not connected to SQL Server. Call connect() first.")
        
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            raise Exception(f"Query execution failed: {e}")
    
    def get_tables(self) -> List[str]:
        """
        List all available tables in the database.
        
        Returns:
            List of table names
        """
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE='BASE TABLE'
        ORDER BY TABLE_NAME
        """
        df = self.execute_query(query)
        return df['TABLE_NAME'].tolist()
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame with column information
        """
        if not self.connection:
            raise Exception("Not connected to SQL Server. Call connect() first.")

        query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        try:
            df = pd.read_sql_query(query, self.connection, params=[table_name])
            return df
        except Exception as e:
            raise Exception(f"Schema query failed: {e}")
    
    def test_connection(self) -> bool:
        """
        Test if the connection is alive.

        Returns:
            True if connection is active, False otherwise
        """
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except (pyodbc.Error, Exception) as e:
            print(f"Connection test failed: {e}")
            return False
    
    def disconnect(self):
        """Close the SQL Server connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("✅ Disconnected from SQL Server")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


