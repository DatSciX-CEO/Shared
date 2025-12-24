"""
Data Comparator Service - Core comparison logic using datacompy.
"""
import pandas as pd
import datacompy
from typing import Optional
import json


class DataComparator:
    """Compares two dataframes and generates comprehensive reports."""
    
    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                 df1_name: str = "File A", df2_name: str = "File B"):
        self.df1 = df1
        self.df2 = df2
        self.df1_name = df1_name
        self.df2_name = df2_name
        self._comparison: Optional[datacompy.Compare] = None
    
    def compare(self, join_columns: list[str], 
                ignore_columns: Optional[list[str]] = None,
                abs_tol: float = 0.0001,
                rel_tol: float = 0.0) -> dict:
        """
        Perform the comparison and return results.
        
        Args:
            join_columns: Columns to use as unique identifier for matching rows
            ignore_columns: Columns to exclude from comparison
            abs_tol: Absolute tolerance for numeric comparisons
            rel_tol: Relative tolerance for numeric comparisons
        """
        df1_compare = self.df1.copy()
        df2_compare = self.df2.copy()
        
        # Remove ignored columns
        if ignore_columns:
            df1_compare = df1_compare.drop(columns=[c for c in ignore_columns if c in df1_compare.columns], errors='ignore')
            df2_compare = df2_compare.drop(columns=[c for c in ignore_columns if c in df2_compare.columns], errors='ignore')
        
        self._comparison = datacompy.Compare(
            df1_compare,
            df2_compare,
            join_columns=join_columns,
            df1_name=self.df1_name,
            df2_name=self.df2_name,
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )
        
        return self._get_comparison_results()
    
    def _get_comparison_results(self) -> dict:
        """Extract comprehensive comparison results."""
        if not self._comparison:
            raise ValueError("Comparison not yet performed. Call compare() first.")
        
        comp = self._comparison
        
        # Get column differences
        cols_only_in_df1 = list(comp.df1_unq_columns())
        cols_only_in_df2 = list(comp.df2_unq_columns())
        common_columns = list(comp.intersect_columns())
        
        # Get row differences
        rows_only_in_df1 = comp.df1_unq_rows.to_dict(orient='records') if len(comp.df1_unq_rows) > 0 else []
        rows_only_in_df2 = comp.df2_unq_rows.to_dict(orient='records') if len(comp.df2_unq_rows) > 0 else []
        
        # Get column-level mismatch details
        column_mismatches = []
        for col in comp.intersect_columns():
            if col not in comp.join_columns:
                mismatch_count = comp.column_stats.get(col, {}).get('unequal_cnt', 0) if hasattr(comp, 'column_stats') else 0
                
                # Calculate mismatch from the comparison directly
                try:
                    if col in comp.intersect_rows.columns:
                        # Check for column mismatch
                        if f"{col}_df1" in comp.intersect_rows.columns and f"{col}_df2" in comp.intersect_rows.columns:
                            mask = comp.intersect_rows[f"{col}_df1"] != comp.intersect_rows[f"{col}_df2"]
                            mismatch_count = mask.sum()
                except Exception:
                    mismatch_count = 0
                
                column_mismatches.append({
                    "column": col,
                    "mismatch_count": int(mismatch_count),
                })
        
        # Get mismatched columns with sample differences
        mismatched_cols_with_samples = []
        for col_info in column_mismatches:
            if col_info["mismatch_count"] > 0:
                mismatched_cols_with_samples.append(col_info["column"])
        
        return {
            "matches": comp.matches(),
            "summary": {
                "df1_name": self.df1_name,
                "df2_name": self.df2_name,
                "df1_rows": len(self.df1),
                "df2_rows": len(self.df2),
                "df1_columns": len(self.df1.columns),
                "df2_columns": len(self.df2.columns),
                "common_rows": len(comp.intersect_rows) if hasattr(comp, 'intersect_rows') else 0,
                "common_columns": len(common_columns),
            },
            "columns": {
                "only_in_df1": cols_only_in_df1,
                "only_in_df2": cols_only_in_df2,
                "common": common_columns,
                "mismatched": mismatched_cols_with_samples,
            },
            "rows": {
                "only_in_df1_count": len(rows_only_in_df1),
                "only_in_df2_count": len(rows_only_in_df2),
                "only_in_df1_sample": rows_only_in_df1[:10],  # First 10 samples
                "only_in_df2_sample": rows_only_in_df2[:10],
            },
            "column_stats": column_mismatches,
            "text_report": comp.report(),
        }
    
    def get_detailed_diff(self, column: str, limit: int = 100) -> list[dict]:
        """Get detailed row-by-row differences for a specific column."""
        if not self._comparison:
            raise ValueError("Comparison not yet performed. Call compare() first.")
        
        comp = self._comparison
        diffs = []
        
        try:
            intersect = comp.intersect_rows
            col_df1 = f"{column}_df1" if f"{column}_df1" in intersect.columns else column
            col_df2 = f"{column}_df2" if f"{column}_df2" in intersect.columns else column
            
            if col_df1 in intersect.columns and col_df2 in intersect.columns:
                mask = intersect[col_df1] != intersect[col_df2]
                diff_rows = intersect[mask].head(limit)
                
                for idx, row in diff_rows.iterrows():
                    diffs.append({
                        "row_index": int(idx) if isinstance(idx, int) else str(idx),
                        "value_in_df1": str(row[col_df1]),
                        "value_in_df2": str(row[col_df2]),
                    })
        except Exception as e:
            pass
        
        return diffs
    
    def get_statistics(self) -> dict:
        """Get comprehensive statistics for both dataframes."""
        stats = {
            "df1": self._get_df_stats(self.df1, self.df1_name),
            "df2": self._get_df_stats(self.df2, self.df2_name),
        }
        return stats
    
    def _get_df_stats(self, df: pd.DataFrame, name: str) -> dict:
        """Get statistics for a single dataframe."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        stats = {
            "name": name,
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "null_counts": df.isnull().sum().to_dict(),
            "null_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_columns": numeric_cols,
            "text_columns": text_cols,
        }
        
        # Add numeric stats
        if numeric_cols:
            stats["numeric_summary"] = df[numeric_cols].describe().to_dict()
        
        # Add text column stats
        text_stats = {}
        for col in text_cols[:10]:  # Limit to first 10 text columns
            text_stats[col] = {
                "unique_values": int(df[col].nunique()),
                "most_common": df[col].value_counts().head(5).to_dict(),
                "avg_length": round(df[col].astype(str).str.len().mean(), 2),
            }
        stats["text_summary"] = text_stats
        
        return stats

