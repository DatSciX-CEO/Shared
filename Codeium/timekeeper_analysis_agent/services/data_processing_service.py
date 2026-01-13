# Copyright 2025 DatSciX
# Data Processing Service

"""Service for data processing and manipulation."""

import pandas as pd
from typing import Dict, Any, Optional


class DataProcessor:
    """Helper class for common data processing operations."""

    @staticmethod
    def calculate_utilization(df: pd.DataFrame, available_hours_per_week: float = 40) -> pd.DataFrame:
        """
        Calculate utilization metrics for timekeepers.

        Args:
            df: DataFrame with timekeeper data
            available_hours_per_week: Expected available hours per week

        Returns:
            DataFrame with utilization metrics added
        """
        result = df.copy()

        # Add week column if not present
        if "date" in result.columns:
            result["week"] = pd.to_datetime(result["date"]).dt.isocalendar().week
            result["year"] = pd.to_datetime(result["date"]).dt.year

        # Calculate weekly hours by timekeeper
        if all(col in result.columns for col in ["timekeeper_id", "week", "year", "hours"]):
            weekly_hours = result.groupby(["timekeeper_id", "year", "week"])["hours"].sum().reset_index()
            weekly_hours["utilization_pct"] = (weekly_hours["hours"] / available_hours_per_week) * 100
            result = result.merge(weekly_hours[["timekeeper_id", "year", "week", "utilization_pct"]],
                                  on=["timekeeper_id", "year", "week"], how="left")

        return result

    @staticmethod
    def calculate_billable_percentage(df: pd.DataFrame, billable_col: str = "billable") -> pd.DataFrame:
        """
        Calculate billable percentage for timekeepers.

        Args:
            df: DataFrame with timekeeper data
            billable_col: Column indicating if hours are billable

        Returns:
            DataFrame with billable percentage added
        """
        result = df.copy()

        if billable_col in result.columns and "hours" in result.columns:
            result["billable_hours"] = result.apply(
                lambda row: row["hours"] if row.get(billable_col, False) else 0,
                axis=1
            )

            # Calculate by timekeeper
            if "timekeeper_id" in result.columns:
                billable_summary = result.groupby("timekeeper_id").agg({
                    "hours": "sum",
                    "billable_hours": "sum"
                }).reset_index()
                billable_summary["billable_pct"] = (
                    billable_summary["billable_hours"] / billable_summary["hours"] * 100
                )
                result = result.merge(
                    billable_summary[["timekeeper_id", "billable_pct"]],
                    on="timekeeper_id",
                    how="left"
                )

        return result

    @staticmethod
    def identify_outliers(
        series: pd.Series,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pd.Series:
        """
        Identify outliers in a pandas Series.

        Args:
            series: Data series to analyze
            method: Method to use ("iqr" or "zscore")
            threshold: Threshold for outlier detection

        Returns:
            Boolean series indicating outliers
        """
        if method == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            return (series < lower) | (series > upper)
        elif method == "zscore":
            z_scores = (series - series.mean()) / series.std()
            return abs(z_scores) > threshold
        else:
            raise ValueError(f"Unknown method: {method}")

    @staticmethod
    def aggregate_by_period(
        df: pd.DataFrame,
        period: str = "week",
        agg_cols: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Aggregate data by time period.

        Args:
            df: DataFrame with date column
            period: Period to aggregate by ("day", "week", "month")
            agg_cols: Dictionary of columns to aggregate and their methods

        Returns:
            Aggregated DataFrame
        """
        if "date" not in df.columns:
            raise ValueError("DataFrame must have 'date' column")

        result = df.copy()
        result["date"] = pd.to_datetime(result["date"])

        if period == "week":
            result["period"] = result["date"].dt.isocalendar().week
            result["period_year"] = result["date"].dt.year
        elif period == "month":
            result["period"] = result["date"].dt.month
            result["period_year"] = result["date"].dt.year
        elif period == "day":
            result["period"] = result["date"]
            result["period_year"] = result["date"].dt.year
        else:
            raise ValueError(f"Unknown period: {period}")

        if agg_cols is None:
            agg_cols = {"hours": "sum", "rate": "mean"}

        groupby_cols = ["period_year", "period"]
        if "timekeeper_id" in result.columns:
            groupby_cols.append("timekeeper_id")

        aggregated = result.groupby(groupby_cols).agg(agg_cols).reset_index()

        return aggregated