# Copyright 2025 DatSciX
# Statistical Analysis Tool

"""Tool for statistical analysis and anomaly detection on timekeeper data."""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional


def calculate_statistics(
    df: pd.DataFrame,
    groupby_col: Optional[str] = None,
    metrics: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate statistical metrics for timekeeper data.

    Args:
        df: pandas DataFrame with timekeeper data
        groupby_col: Optional column to group by (e.g., "timekeeper_id")
        metrics: List of metrics to calculate (default: all common metrics)

    Returns:
        Dictionary with calculated statistics
    """
    if metrics is None:
        metrics = ["mean", "median", "std", "min", "max", "sum", "count"]

    results = {}

    if groupby_col and groupby_col in df.columns:
        # Group-level statistics
        if "hours" in df.columns:
            hours_stats = df.groupby(groupby_col)["hours"].agg(metrics)
            results["hours_by_" + groupby_col] = hours_stats.to_dict()

        if "rate" in df.columns:
            rate_stats = df.groupby(groupby_col)["rate"].agg(metrics)
            results["rate_by_" + groupby_col] = rate_stats.to_dict()

        if "hours" in df.columns and "rate" in df.columns:
            df["revenue"] = df["hours"] * df["rate"]
            revenue_stats = df.groupby(groupby_col)["revenue"].agg(metrics)
            results["revenue_by_" + groupby_col] = revenue_stats.to_dict()
    else:
        # Overall statistics
        if "hours" in df.columns:
            results["hours"] = df["hours"].describe().to_dict()

        if "rate" in df.columns:
            results["rate"] = df["rate"].describe().to_dict()

        if "hours" in df.columns and "rate" in df.columns:
            df["revenue"] = df["hours"] * df["rate"]
            results["revenue"] = df["revenue"].describe().to_dict()

    return results


def detect_anomalies(
    df: pd.DataFrame,
    column: str,
    method: str = "zscore",
    threshold: float = 3.0,
    groupby_col: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect anomalies in timekeeper data using statistical methods.

    Args:
        df: pandas DataFrame with timekeeper data
        column: Column name to analyze for anomalies
        method: Detection method ("zscore", "iqr", "mad")
        threshold: Threshold for anomaly detection (e.g., 3 for 3 std devs)
        groupby_col: Optional column to group by for context-aware detection

    Returns:
        Dictionary containing:
        - anomalies: DataFrame of detected anomalies
        - summary: Summary statistics
        - severity_counts: Count by severity level
    """
    if column not in df.columns:
        return {
            "anomalies": pd.DataFrame(),
            "summary": {},
            "severity_counts": {},
            "message": f"Column '{column}' not found in data"
        }

    df_copy = df.copy()
    anomalies = []

    if groupby_col and groupby_col in df.columns:
        # Context-aware anomaly detection within groups
        for group_id, group_df in df_copy.groupby(groupby_col):
            group_anomalies = _detect_anomalies_in_series(
                group_df,
                column,
                method,
                threshold,
                context={"group": groupby_col, "group_id": group_id}
            )
            anomalies.extend(group_anomalies)
    else:
        # Global anomaly detection
        anomalies = _detect_anomalies_in_series(df_copy, column, method, threshold)

    # Create anomalies DataFrame
    if anomalies:
        anomaly_df = pd.DataFrame(anomalies)

        # Calculate severity based on deviation magnitude
        if "deviation" in anomaly_df.columns:
            anomaly_df["severity"] = anomaly_df["deviation"].apply(_assign_severity, threshold=threshold)
    else:
        anomaly_df = pd.DataFrame()

    # Generate summary
    summary = {
        "total_records": len(df),
        "anomalies_detected": len(anomalies),
        "anomaly_rate": len(anomalies) / len(df) * 100 if len(df) > 0 else 0,
        "method": method,
        "threshold": threshold,
    }

    # Count by severity
    severity_counts = {}
    if not anomaly_df.empty and "severity" in anomaly_df.columns:
        severity_counts = anomaly_df["severity"].value_counts().to_dict()

    return {
        "anomalies": anomaly_df,
        "summary": summary,
        "severity_counts": severity_counts,
        "message": f"Detected {len(anomalies)} anomalies using {method} method"
    }


def _detect_anomalies_in_series(
    df: pd.DataFrame,
    column: str,
    method: str,
    threshold: float,
    context: Optional[Dict] = None
) -> List[Dict]:
    """Helper function to detect anomalies in a data series."""
    anomalies = []
    series = df[column].dropna()

    if len(series) == 0:
        return anomalies

    if method == "zscore":
        # Z-score method
        mean = series.mean()
        std = series.std()

        if std == 0:
            return anomalies

        z_scores = np.abs((series - mean) / std)

        for idx in series.index:
            z_score = z_scores[idx]
            if z_score > threshold:
                anomaly = {
                    "index": int(idx),
                    "value": float(series[idx]),
                    "expected_mean": float(mean),
                    "deviation": float(z_score),
                    "deviation_type": "zscore",
                }
                if context:
                    anomaly.update(context)

                # Add other columns for context
                for col in df.columns:
                    if col != column:
                        anomaly[col] = df.loc[idx, col]

                anomalies.append(anomaly)

    elif method == "iqr":
        # Interquartile Range method
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        outliers = series[(series < lower_bound) | (series > upper_bound)]

        for idx in outliers.index:
            value = series[idx]
            deviation = abs(value - Q1) / IQR if value < Q1 else abs(value - Q3) / IQR

            anomaly = {
                "index": int(idx),
                "value": float(value),
                "expected_range": f"[{lower_bound:.2f}, {upper_bound:.2f}]",
                "deviation": float(deviation),
                "deviation_type": "iqr",
            }
            if context:
                anomaly.update(context)

            for col in df.columns:
                if col != column:
                    anomaly[col] = df.loc[idx, col]

            anomalies.append(anomaly)

    elif method == "mad":
        # Median Absolute Deviation method
        median = series.median()
        mad = np.median(np.abs(series - median))

        if mad == 0:
            return anomalies

        modified_z_scores = 0.6745 * (series - median) / mad

        for idx in series.index:
            mod_z_score = abs(modified_z_scores[idx])
            if mod_z_score > threshold:
                anomaly = {
                    "index": int(idx),
                    "value": float(series[idx]),
                    "expected_median": float(median),
                    "deviation": float(mod_z_score),
                    "deviation_type": "mad",
                }
                if context:
                    anomaly.update(context)

                for col in df.columns:
                    if col != column:
                        anomaly[col] = df.loc[idx, col]

                anomalies.append(anomaly)

    return anomalies


def _assign_severity(deviation: float, threshold: float) -> str:
    """Assign severity level based on deviation magnitude."""
    if deviation >= threshold * 2:
        return "critical"
    elif deviation >= threshold * 1.5:
        return "high"
    elif deviation >= threshold:
        return "medium"
    else:
        return "low"