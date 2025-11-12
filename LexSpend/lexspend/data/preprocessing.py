"""
Data preprocessing and validation for legal spend data
"""
import pandas as pd
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

# Required columns for MVP
REQUIRED_COLUMNS = [
    "Position Title",  # or "Timekeeper", "Role"
    "Units",  # or "Hours", "Billable Hours"
    "Bill Rate",  # or "Rate", "Hourly Rate"
    "Cost",  # or "Total Cost", "Amount"
    "Line Item Description",  # or "Description", "Activity"
    "Type of Case",  # or "Case Type", "Matter Type"
]

# Alternative column name mappings
COLUMN_MAPPINGS = {
    "Position Title": ["Timekeeper", "Role", "Position", "Title", "Timekeeper Title"],
    "Units": ["Hours", "Billable Hours", "Units Billed", "Quantity"],
    "Bill Rate": ["Rate", "Hourly Rate", "Billing Rate", "Rate per Hour"],
    "Cost": ["Total Cost", "Amount", "Total Amount", "Line Item Cost"],
    "Line Item Description": ["Description", "Activity", "Task Description", "Work Description"],
    "Type of Case": ["Case Type", "Matter Type", "Matter Category", "Case Category"],
}


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to standard required column names.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with normalized column names
    """
    df_normalized = df.copy()
    column_mapping = {}
    
    for standard_name, alternatives in COLUMN_MAPPINGS.items():
        # Check if standard name exists
        if standard_name in df.columns:
            continue
        
        # Check for alternatives
        for alt_name in alternatives:
            if alt_name in df.columns:
                column_mapping[alt_name] = standard_name
                break
    
    if column_mapping:
        df_normalized = df_normalized.rename(columns=column_mapping)
        logger.info(f"Normalized columns: {column_mapping}")
    
    return df_normalized


def validate_data(df: pd.DataFrame) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Validate that the DataFrame has required columns and valid data.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (is_valid, message, normalized_df)
    """
    if df.empty:
        return False, "DataFrame is empty", None
    
    # Normalize column names
    df_normalized = normalize_column_names(df)
    
    # Check for required columns
    missing_columns = []
    for col in REQUIRED_COLUMNS:
        if col not in df_normalized.columns:
            missing_columns.append(col)
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}", None
    
    # Validate data types
    numeric_columns = ["Units", "Bill Rate", "Cost"]
    for col in numeric_columns:
        if col in df_normalized.columns:
            # Try to convert to numeric
            df_normalized[col] = pd.to_numeric(df_normalized[col], errors='coerce')
            # Check for all NaN
            if df_normalized[col].isna().all():
                return False, f"Column '{col}' contains no valid numeric values", None
    
    # Check for negative values in cost/rate (might be valid, but flag it)
    if "Cost" in df_normalized.columns:
        negative_costs = (df_normalized["Cost"] < 0).sum()
        if negative_costs > 0:
            logger.warning(f"Found {negative_costs} rows with negative costs")
    
    return True, "Data validation passed", df_normalized


def handle_missing_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing data in the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with missing data handled
    """
    df_cleaned = df.copy()
    
    # For Line Item Description, fill empty with placeholder
    if "Line Item Description" in df_cleaned.columns:
        df_cleaned["Line Item Description"] = df_cleaned["Line Item Description"].fillna("[No Description]")
    
    # For numeric columns, we'll keep NaN for now (GNN can handle it)
    # But log warnings
    numeric_columns = ["Units", "Bill Rate", "Cost"]
    for col in numeric_columns:
        if col in df_cleaned.columns:
            missing_count = df_cleaned[col].isna().sum()
            if missing_count > 0:
                logger.warning(f"Column '{col}' has {missing_count} missing values")
    
    return df_cleaned


def prepare_data_for_analysis(file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Complete data preparation pipeline: load, validate, and clean.
    
    Args:
        file_path: Path to CSV or Excel file
        
    Returns:
        Tuple of (success, message, dataframe)
    """
    try:
        # Load file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            return False, f"Unsupported file type. Expected CSV or Excel file.", None
        
        # Validate
        is_valid, message, df_normalized = validate_data(df)
        if not is_valid:
            return False, message, None
        
        # Handle missing data
        df_cleaned = handle_missing_data(df_normalized)
        
        return True, "Data loaded and validated successfully", df_cleaned
        
    except FileNotFoundError:
        return False, f"File not found: {file_path}", None
    except Exception as e:
        return False, f"Error processing file: {type(e).__name__}: {str(e)}", None

