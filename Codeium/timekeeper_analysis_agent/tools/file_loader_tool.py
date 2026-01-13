# Copyright 2025 DatSciX
# File Loader Tool

"""Tool for loading timekeeper data from various file formats."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any


def load_timekeeper_file(file_path: str, file_format: str = None) -> Dict[str, Any]:
    """
    Load timekeeper data from CSV, Excel, or Parquet file.

    Args:
        file_path: Path to the data file
        file_format: Optional file format override ("csv", "excel", "parquet")
                    If not provided, determined from file extension

    Returns:
        Dictionary containing:
        - data: pandas DataFrame with loaded data
        - metadata: dict with file info (rows, columns, format)
        - success: boolean indicating if load was successful
        - message: string with status or error message
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {
                "data": None,
                "metadata": {},
                "success": False,
                "message": f"File not found: {file_path}"
            }

        # Determine format from extension if not provided
        if file_format is None:
            ext = path.suffix.lower()
            format_map = {
                ".csv": "csv",
                ".xlsx": "excel",
                ".xls": "excel",
                ".parquet": "parquet",
            }
            file_format = format_map.get(ext)

            if file_format is None:
                return {
                    "data": None,
                    "metadata": {},
                    "success": False,
                    "message": f"Unsupported file format: {ext}. Supported: .csv, .xlsx, .xls, .parquet"
                }

        # Load data based on format
        if file_format == "csv":
            df = pd.read_csv(file_path)
        elif file_format == "excel":
            df = pd.read_excel(file_path)
        elif file_format == "parquet":
            df = pd.read_parquet(file_path)
        else:
            return {
                "data": None,
                "metadata": {},
                "success": False,
                "message": f"Unsupported format: {file_format}"
            }

        # Standardize column names (lowercase, strip whitespace)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # Gather metadata
        metadata = {
            "file_path": str(path),
            "file_format": file_format,
            "file_size_mb": path.stat().st_size / (1024 * 1024),
            "rows": len(df),
            "columns": list(df.columns),
            "column_count": len(df.columns),
        }

        return {
            "data": df,
            "metadata": metadata,
            "success": True,
            "message": f"Successfully loaded {len(df)} records from {file_format.upper()} file"
        }

    except Exception as e:
        return {
            "data": None,
            "metadata": {},
            "success": False,
            "message": f"Error loading file: {str(e)}"
        }