"""
Data Validation for Legal Spend Data
Ensures data quality and schema compliance
"""
import pandas as pd
from typing import Tuple, List
import sys
import os

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import REQUIRED_COLUMNS, OPTIONAL_COLUMNS


def validate_legal_spend_data(df: pd.DataFrame) -> Tuple[bool, str, pd.DataFrame]:
    """
    Validate legal spend data for required columns and data quality.
    
    Args:
        df: pandas DataFrame to validate
        
    Returns:
        Tuple of (success: bool, message: str, cleaned_df: pd.DataFrame)
    """
    try:
        # Check if DataFrame is empty
        if df.empty:
            return False, "DataFrame is empty", df
        
        # Normalize column names (lowercase, strip whitespace)
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        # Check for required columns (flexible matching)
        missing_columns = []
        column_mapping = {}
        
        for req_col in REQUIRED_COLUMNS:
            # Try to find column with similar name
            matches = [col for col in df.columns if req_col.lower() in col.lower()]
            if matches:
                column_mapping[matches[0]] = req_col
            else:
                missing_columns.append(req_col)
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}", df
        
        # Rename columns to standard names
        df = df.rename(columns=column_mapping)
        
        # Validate data types
        # Convert amount to numeric
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isna().all():
                return False, "Amount column contains no valid numeric values", df
        
        # Convert date to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            if df['date'].isna().all():
                return False, "Date column contains no valid date values", df
        
        # Remove rows with missing critical data
        initial_rows = len(df)
        df = df.dropna(subset=['amount', 'law_firm'])
        rows_removed = initial_rows - len(df)
        
        if df.empty:
            return False, "No valid rows remaining after removing missing data", df
        
        message = f"✅ Validation successful. {len(df)} rows validated"
        if rows_removed > 0:
            message += f" ({rows_removed} rows removed due to missing data)"
        
        return True, message, df
        
    except Exception as e:
        return False, f"Validation error: {str(e)}", df


def get_data_quality_report(df: pd.DataFrame) -> str:
    """
    Generate a data quality report for the DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        String report of data quality metrics
    """
    report = []
    report.append("=== Data Quality Report ===\n")
    report.append(f"Total Rows: {len(df)}")
    report.append(f"Total Columns: {len(df.columns)}")
    report.append(f"\nColumns: {', '.join(df.columns.tolist())}\n")
    
    # Missing data analysis
    report.append("Missing Data:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    for col in df.columns:
        if missing[col] > 0:
            report.append(f"  - {col}: {missing[col]} ({missing_pct[col]}%)")
    
    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        report.append(f"\nNumeric Columns Summary:")
        for col in numeric_cols:
            report.append(f"  - {col}:")
            report.append(f"    Min: {df[col].min():.2f}")
            report.append(f"    Max: {df[col].max():.2f}")
            report.append(f"    Mean: {df[col].mean():.2f}")
            report.append(f"    Median: {df[col].median():.2f}")
    
    return "\n".join(report)


