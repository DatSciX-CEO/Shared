# Copyright 2025 DatSciX
# Data Validator Tool

"""Tool for validating timekeeper data structure and content."""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any


def validate_timekeeper_data(
    df: pd.DataFrame,
    required_columns: List[str] = None,
    optional_columns: List[str] = None
) -> Dict[str, Any]:
    """
    Validate timekeeper data structure, types, and content quality.

    Args:
        df: pandas DataFrame to validate
        required_columns: List of required column names
        optional_columns: List of optional column names

    Returns:
        Dictionary containing:
        - is_valid: boolean indicating if data passes all critical checks
        - issues: list of validation issues found
        - warnings: list of non-critical warnings
        - summary: dict with data quality metrics
        - cleaned_data: DataFrame with basic cleaning applied
    """
    if required_columns is None:
        required_columns = ["timekeeper_id", "date", "hours", "rate"]

    if optional_columns is None:
        optional_columns = ["matter_id", "task_code", "description", "client_id"]

    issues = []
    warnings = []
    cleaned_df = df.copy()

    # 1. Check required columns
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        issues.append(f"Missing required columns: {', '.join(missing_required)}")

    # 2. Check column data types and clean
    if "hours" in cleaned_df.columns:
        try:
            cleaned_df["hours"] = pd.to_numeric(cleaned_df["hours"], errors="coerce")
            null_hours = cleaned_df["hours"].isna().sum()
            if null_hours > 0:
                warnings.append(f"{null_hours} records have invalid hours values")
        except Exception as e:
            issues.append(f"Error converting hours to numeric: {str(e)}")

    if "rate" in cleaned_df.columns:
        try:
            cleaned_df["rate"] = pd.to_numeric(cleaned_df["rate"], errors="coerce")
            null_rates = cleaned_df["rate"].isna().sum()
            if null_rates > 0:
                warnings.append(f"{null_rates} records have invalid rate values")
        except Exception as e:
            issues.append(f"Error converting rate to numeric: {str(e)}")

    if "date" in cleaned_df.columns:
        try:
            cleaned_df["date"] = pd.to_datetime(cleaned_df["date"], errors="coerce")
            null_dates = cleaned_df["date"].isna().sum()
            if null_dates > 0:
                warnings.append(f"{null_dates} records have invalid date values")
        except Exception as e:
            issues.append(f"Error converting date to datetime: {str(e)}")

    # 3. Check for missing values in required columns
    for col in required_columns:
        if col in cleaned_df.columns:
            missing = cleaned_df[col].isna().sum()
            if missing > 0:
                pct = (missing / len(cleaned_df)) * 100
                if pct > 10:
                    issues.append(f"{col}: {missing} missing values ({pct:.1f}%)")
                else:
                    warnings.append(f"{col}: {missing} missing values ({pct:.1f}%)")

    # 4. Check data ranges and anomalies
    if "hours" in cleaned_df.columns:
        negative_hours = (cleaned_df["hours"] < 0).sum()
        if negative_hours > 0:
            issues.append(f"{negative_hours} records have negative hours")

        zero_hours = (cleaned_df["hours"] == 0).sum()
        if zero_hours > 0:
            warnings.append(f"{zero_hours} records have zero hours")

        extreme_hours = (cleaned_df["hours"] > 24).sum()
        if extreme_hours > 0:
            warnings.append(f"{extreme_hours} records have hours > 24 per day")

    if "rate" in cleaned_df.columns:
        zero_rates = (cleaned_df["rate"] == 0).sum()
        if zero_rates > 0:
            warnings.append(f"{zero_rates} records have zero billing rate")

        negative_rates = (cleaned_df["rate"] < 0).sum()
        if negative_rates > 0:
            issues.append(f"{negative_rates} records have negative rates")

    if "date" in cleaned_df.columns:
        future_dates = (cleaned_df["date"] > pd.Timestamp.now()).sum()
        if future_dates > 0:
            warnings.append(f"{future_dates} records have future dates")

    # 5. Check for duplicates
    if all(col in cleaned_df.columns for col in ["timekeeper_id", "date"]):
        duplicates = cleaned_df.duplicated(subset=["timekeeper_id", "date", "hours"]).sum()
        if duplicates > 0:
            warnings.append(f"{duplicates} potential duplicate records found")

    # 6. Generate summary statistics
    summary = {
        "total_records": len(cleaned_df),
        "valid_records": len(cleaned_df.dropna(subset=required_columns)),
        "date_range": None,
        "unique_timekeepers": None,
        "total_hours": None,
        "total_revenue": None,
    }

    if "date" in cleaned_df.columns:
        valid_dates = cleaned_df["date"].dropna()
        if len(valid_dates) > 0:
            summary["date_range"] = {
                "start": valid_dates.min().strftime("%Y-%m-%d"),
                "end": valid_dates.max().strftime("%Y-%m-%d"),
            }

    if "timekeeper_id" in cleaned_df.columns:
        summary["unique_timekeepers"] = cleaned_df["timekeeper_id"].nunique()

    if "hours" in cleaned_df.columns:
        summary["total_hours"] = float(cleaned_df["hours"].sum())

    if "hours" in cleaned_df.columns and "rate" in cleaned_df.columns:
        cleaned_df["revenue"] = cleaned_df["hours"] * cleaned_df["rate"]
        summary["total_revenue"] = float(cleaned_df["revenue"].sum())

    # Determine overall validity
    is_valid = len(issues) == 0

    return {
        "is_valid": is_valid,
        "issues": issues,
        "warnings": warnings,
        "summary": summary,
        "cleaned_data": cleaned_df if is_valid or len(issues) < 3 else None,
    }