"""
Data Ingestion Tools for ADK
Reads CSV, Parquet, and SQL Server data
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
from google.adk.tools import FunctionTool
import sys
import os

# Import data utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_connector import SQLServerConnector
from data.data_validator import validate_legal_spend_data


def read_csv_file(file_path: str) -> str:
    """
    Reads a CSV file and returns a summary of legal spend data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        String summary of the file contents including shape, columns, and preview
    """
    try:
        df = pd.read_csv(file_path)
        
        # Validate data
        success, message, df = validate_legal_spend_data(df)
        
        summary = []
        summary.append(f"✅ CSV loaded successfully: {file_path}")
        summary.append(f"Validation: {message}")
        summary.append(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")
        summary.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Add data preview
        summary.append(f"\nFirst 5 rows:")
        summary.append(df.head().to_string())
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary.append(f"\n\nBasic Statistics:")
            if 'amount' in df.columns:
                summary.append(f"Total Spend: ${df['amount'].sum():,.2f}")
                summary.append(f"Average Amount: ${df['amount'].mean():,.2f}")
                summary.append(f"Min Amount: ${df['amount'].min():,.2f}")
                summary.append(f"Max Amount: ${df['amount'].max():,.2f}")
        
        # Add unique law firms count
        if 'law_firm' in df.columns:
            summary.append(f"\nUnique Law Firms: {df['law_firm'].nunique()}")
        
        return "\n".join(summary)
        
    except FileNotFoundError:
        return f"❌ Error: File not found at path: {file_path}"
    except Exception as e:
        return f"❌ Error reading CSV file: {type(e).__name__}: {str(e)}"


def read_parquet_file(file_path: str) -> str:
    """
    Reads a Parquet file and returns a summary of legal spend data.
    
    Args:
        file_path: Path to the Parquet file
        
    Returns:
        String summary of the file contents
    """
    try:
        df = pd.read_parquet(file_path)
        
        # Validate data
        success, message, df = validate_legal_spend_data(df)
        
        summary = []
        summary.append(f"✅ Parquet file loaded successfully: {file_path}")
        summary.append(f"Validation: {message}")
        summary.append(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")
        summary.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Add data preview
        summary.append(f"\nFirst 5 rows:")
        summary.append(df.head().to_string())
        
        # Add basic statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary.append(f"\n\nBasic Statistics:")
            if 'amount' in df.columns:
                summary.append(f"Total Spend: ${df['amount'].sum():,.2f}")
                summary.append(f"Average Amount: ${df['amount'].mean():,.2f}")
        
        # Add unique law firms count
        if 'law_firm' in df.columns:
            summary.append(f"\nUnique Law Firms: {df['law_firm'].nunique()}")
        
        return "\n".join(summary)
        
    except FileNotFoundError:
        return f"❌ Error: File not found at path: {file_path}"
    except Exception as e:
        return f"❌ Error reading Parquet file: {type(e).__name__}: {str(e)}"


def read_sql_server_data(query: str = None, table_name: str = None) -> str:
    """
    Reads data from SQL Server and returns a summary.
    
    Args:
        query: SQL query to execute (optional)
        table_name: Table name to read (optional, if query not provided)
        
    Returns:
        String summary of the query results
    """
    try:
        if not query and not table_name:
            return "❌ Error: Must provide either 'query' or 'table_name' parameter"
        
        connector = SQLServerConnector()
        
        # Connect to SQL Server
        if not connector.connect():
            return "❌ Error: Failed to connect to SQL Server. Check configuration."
        
        # Execute query or read table
        if query:
            df = connector.execute_query(query)
        else:
            df = connector.execute_query(f"SELECT * FROM {table_name}")
        
        connector.disconnect()
        
        # Validate data
        success, message, df = validate_legal_spend_data(df)
        
        summary = []
        summary.append(f"✅ SQL Server data loaded successfully")
        if table_name:
            summary.append(f"Table: {table_name}")
        summary.append(f"Validation: {message}")
        summary.append(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")
        summary.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Add data preview
        summary.append(f"\nFirst 5 rows:")
        summary.append(df.head().to_string())
        
        # Add basic statistics
        if 'amount' in df.columns:
            summary.append(f"\n\nBasic Statistics:")
            summary.append(f"Total Spend: ${df['amount'].sum():,.2f}")
            summary.append(f"Average Amount: ${df['amount'].mean():,.2f}")
        
        # Add unique law firms count
        if 'law_firm' in df.columns:
            summary.append(f"\nUnique Law Firms: {df['law_firm'].nunique()}")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"❌ Error reading SQL Server data: {type(e).__name__}: {str(e)}"


def list_sql_tables() -> str:
    """
    Lists all available tables in the configured SQL Server database.
    
    Returns:
        String list of table names
    """
    try:
        connector = SQLServerConnector()
        
        if not connector.connect():
            return "❌ Error: Failed to connect to SQL Server"
        
        tables = connector.get_tables()
        connector.disconnect()
        
        if not tables:
            return "No tables found in the database"
        
        summary = []
        summary.append(f"✅ Found {len(tables)} tables in SQL Server database:")
        for i, table in enumerate(tables, 1):
            summary.append(f"{i}. {table}")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"❌ Error listing SQL tables: {str(e)}"


# Create FunctionTool wrappers
# FunctionTool uses the function name and docstring automatically for description
ReadCsvTool = FunctionTool(func=read_csv_file)
ReadParquetTool = FunctionTool(func=read_parquet_file)
ReadSqlServerTool = FunctionTool(func=read_sql_server_data)
ListSqlTablesTool = FunctionTool(func=list_sql_tables)


