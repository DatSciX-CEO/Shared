"""
File Reader Tool for ADK - Reads CSV and Excel files
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
from google.adk.tools import FunctionTool


def read_file(file_path: str) -> str:
    """
    Reads a CSV or Excel file and returns a summary.

    Args:
        file_path: The path to the CSV or Excel file.

    Returns:
        A string summary of the file contents including shape, columns, and preview.
    """
    try:
        # Read the file based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            return f"Error: Unsupported file type. Please provide a CSV or Excel file (.csv, .xls, .xlsx)."

        # Generate summary
        summary = []
        summary.append(f"File loaded successfully: {file_path}")
        summary.append(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        summary.append(f"\nColumns: {', '.join(df.columns.tolist())}")
        summary.append(f"\nFirst 5 rows:")
        summary.append(df.head().to_string())
        
        # Add data types
        summary.append(f"\n\nData types:")
        summary.append(df.dtypes.to_string())
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary.append(f"\n\nBasic statistics for numeric columns:")
            summary.append(df[numeric_cols].describe().to_string())

        return "\n".join(summary)
        
    except FileNotFoundError:
        return f"Error: File not found at path: {file_path}"
    except Exception as e:
        return f"Error reading file: {type(e).__name__}: {str(e)}"


# Create FunctionTool wrapper
# FunctionTool uses the function name and docstring automatically for description
FileReaderTool = FunctionTool(func=read_file)
