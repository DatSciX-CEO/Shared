"""
Data Quality Checker Service - Comprehensive data quality analysis.
Validates data integrity, consistency, and completeness.
"""
import pandas as pd
import numpy as np
from typing import Optional
from collections import defaultdict
import re
from datetime import datetime

# Import centralized config
from config import QUALITY_FORMAT_PATTERNS


class QualityChecker:
    """
    Performs comprehensive data quality checks on dataframes.
    Analyzes:
    - Completeness (null/missing values)
    - Uniqueness (duplicates)
    - Validity (format consistency)
    - Consistency (cross-column rules)
    - Outliers (statistical anomalies)
    """
    
    # Use centralized format patterns from config
    FORMAT_PATTERNS = QUALITY_FORMAT_PATTERNS
    
    def __init__(self, df: pd.DataFrame, name: str = "Dataset"):
        """
        Initialize with a dataframe to check.
        
        Args:
            df: DataFrame to analyze
            name: Name identifier for the dataset
        """
        self.df = df
        self.name = name
        self._results: Optional[dict] = None
    
    def check_all(self) -> dict:
        """
        Run all quality checks and return comprehensive results.
        
        Returns:
            Complete quality analysis report
        """
        completeness = self._check_completeness()
        uniqueness = self._check_uniqueness()
        validity = self._check_validity()
        consistency = self._check_consistency()
        outliers = self._detect_outliers()
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            completeness, uniqueness, validity, consistency, outliers
        )
        
        self._results = {
            "dataset_name": self.name,
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "quality_score": quality_score,
            "completeness": completeness,
            "uniqueness": uniqueness,
            "validity": validity,
            "consistency": consistency,
            "outliers": outliers,
            "summary": self._generate_summary(
                completeness, uniqueness, validity, consistency, outliers
            ),
            "recommendations": self._generate_recommendations(
                completeness, uniqueness, validity, outliers
            ),
        }
        
        return self._results
    
    def _check_completeness(self) -> dict:
        """Check for missing/null values."""
        total_cells = len(self.df) * len(self.df.columns)
        total_nulls = int(self.df.isnull().sum().sum())
        
        column_completeness = {}
        for col in self.df.columns:
            null_count = int(self.df[col].isnull().sum())
            column_completeness[col] = {
                "null_count": null_count,
                "null_percentage": round(null_count / len(self.df) * 100, 2) if len(self.df) > 0 else 0,
                "complete_count": len(self.df) - null_count,
                "is_complete": null_count == 0,
            }
        
        # Find completely null columns
        empty_columns = [col for col, info in column_completeness.items() 
                        if info["null_percentage"] == 100]
        
        # Find columns with high null percentage
        high_null_columns = [col for col, info in column_completeness.items()
                           if 50 <= info["null_percentage"] < 100]
        
        return {
            "total_cells": total_cells,
            "total_nulls": total_nulls,
            "overall_completeness": round((1 - total_nulls / total_cells) * 100, 2) if total_cells > 0 else 100,
            "column_completeness": column_completeness,
            "empty_columns": empty_columns,
            "high_null_columns": high_null_columns,
            "complete_columns": [col for col, info in column_completeness.items() 
                                if info["is_complete"]],
        }
    
    def _check_uniqueness(self) -> dict:
        """Check for duplicate values and rows."""
        # Full row duplicates
        duplicate_rows = int(self.df.duplicated().sum())
        duplicate_indices = self.df[self.df.duplicated(keep=False)].index.tolist()[:20]
        
        # Column-level uniqueness
        column_uniqueness = {}
        for col in self.df.columns:
            unique_count = int(self.df[col].nunique())
            column_uniqueness[col] = {
                "unique_count": unique_count,
                "unique_percentage": round(unique_count / len(self.df) * 100, 2) if len(self.df) > 0 else 0,
                "duplicate_count": len(self.df) - unique_count,
                "is_unique": unique_count == len(self.df),
                "cardinality": "high" if unique_count > len(self.df) * 0.9 else 
                              "medium" if unique_count > len(self.df) * 0.5 else "low",
            }
        
        # Find potential ID columns (high uniqueness)
        potential_id_columns = [col for col, info in column_uniqueness.items()
                               if info["is_unique"] or info["unique_percentage"] > 95]
        
        # Find low cardinality columns (likely categorical)
        categorical_columns = [col for col, info in column_uniqueness.items()
                              if info["cardinality"] == "low" and info["unique_count"] <= 20]
        
        return {
            "duplicate_row_count": duplicate_rows,
            "duplicate_row_percentage": round(duplicate_rows / len(self.df) * 100, 2) if len(self.df) > 0 else 0,
            "duplicate_row_indices_sample": duplicate_indices,
            "column_uniqueness": column_uniqueness,
            "potential_id_columns": potential_id_columns,
            "categorical_columns": categorical_columns,
        }
    
    def _check_validity(self) -> dict:
        """Check data format validity and consistency."""
        validity_results = {}
        
        for col in self.df.columns:
            col_validity = {
                "dtype": str(self.df[col].dtype),
                "format_checks": {},
                "issues": [],
            }
            
            # Skip if column is all null
            if self.df[col].isnull().all():
                validity_results[col] = col_validity
                continue
            
            sample = self.df[col].dropna()
            
            # For string columns, check format patterns
            if self.df[col].dtype == 'object':
                sample_str = sample.astype(str)
                
                # Auto-detect likely format based on column name
                detected_format = self._detect_likely_format(col)
                
                # Check against common patterns
                for pattern_name, pattern in self.FORMAT_PATTERNS.items():
                    matches = sample_str.str.match(pattern, na=False)
                    match_count = int(matches.sum())
                    
                    if match_count > len(sample) * 0.5:  # More than 50% match
                        col_validity["format_checks"][pattern_name] = {
                            "match_count": match_count,
                            "match_percentage": round(match_count / len(sample) * 100, 2),
                            "non_matching_samples": sample_str[~matches].head(5).tolist(),
                        }
                
                # Check for mixed case consistency
                case_analysis = self._analyze_case_consistency(sample_str)
                col_validity["case_consistency"] = case_analysis
                
                # Check for whitespace issues
                whitespace_issues = self._check_whitespace_issues(sample_str)
                if whitespace_issues:
                    col_validity["issues"].append(whitespace_issues)
            
            # For numeric columns, check for string contamination
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                # Check for negative values where unexpected
                if (sample < 0).any():
                    neg_count = int((sample < 0).sum())
                    col_validity["issues"].append({
                        "type": "negative_values",
                        "count": neg_count,
                        "message": f"{neg_count} negative values found",
                    })
            
            validity_results[col] = col_validity
        
        return validity_results
    
    def _detect_likely_format(self, column_name: str) -> Optional[str]:
        """Detect likely format based on column name."""
        col_lower = column_name.lower()
        
        if 'email' in col_lower or 'e_mail' in col_lower:
            return 'email'
        elif 'phone' in col_lower or 'tel' in col_lower or 'mobile' in col_lower:
            return 'phone'
        elif 'date' in col_lower or 'time' in col_lower:
            return 'date'
        elif 'url' in col_lower or 'link' in col_lower:
            return 'url'
        elif 'zip' in col_lower or 'postal' in col_lower:
            return 'zip'
        elif 'uuid' in col_lower or 'guid' in col_lower:
            return 'uuid'
        
        return None
    
    def _analyze_case_consistency(self, series: pd.Series) -> dict:
        """Analyze case consistency in string column."""
        if len(series) == 0:
            return {"consistent": True, "pattern": "empty"}
        
        upper_count = sum(1 for s in series if str(s).isupper())
        lower_count = sum(1 for s in series if str(s).islower())
        title_count = sum(1 for s in series if str(s).istitle())
        
        total = len(series)
        
        if upper_count > total * 0.9:
            return {"consistent": True, "pattern": "UPPER"}
        elif lower_count > total * 0.9:
            return {"consistent": True, "pattern": "lower"}
        elif title_count > total * 0.9:
            return {"consistent": True, "pattern": "Title"}
        else:
            return {
                "consistent": False, 
                "pattern": "mixed",
                "distribution": {
                    "upper": round(upper_count / total * 100, 1),
                    "lower": round(lower_count / total * 100, 1),
                    "title": round(title_count / total * 100, 1),
                },
            }
    
    def _check_whitespace_issues(self, series: pd.Series) -> Optional[dict]:
        """Check for whitespace issues in string column."""
        leading_ws = series.str.match(r'^\s+', na=False).sum()
        trailing_ws = series.str.match(r'\s+$', na=False).sum()
        multiple_ws = series.str.contains(r'\s{2,}', na=False).sum()
        
        if leading_ws > 0 or trailing_ws > 0 or multiple_ws > 0:
            return {
                "type": "whitespace_issues",
                "leading_whitespace": int(leading_ws),
                "trailing_whitespace": int(trailing_ws),
                "multiple_spaces": int(multiple_ws),
                "message": "Whitespace inconsistencies detected",
            }
        
        return None
    
    def _check_consistency(self) -> dict:
        """Check for data consistency and relationships."""
        consistency_checks = []
        
        # Check for columns that might be related
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        # Check if any column sums to another (e.g., subtotal + tax = total)
        if len(numeric_cols) >= 2:
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    # Check correlation
                    correlation = self.df[col1].corr(self.df[col2])
                    if abs(correlation) > 0.95:
                        consistency_checks.append({
                            "type": "high_correlation",
                            "columns": [col1, col2],
                            "correlation": round(correlation, 3),
                            "message": f"High correlation ({correlation:.2f}) between {col1} and {col2}",
                        })
        
        # Check for date columns that should be ordered
        date_cols = []
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(self.df[col], errors='raise')
                    date_cols.append(col)
                except (ValueError, TypeError, pd.errors.ParserError):
                    # Column is not a valid date format
                    pass
        
        if len(date_cols) >= 2:
            # Check if start < end pattern exists
            for i, col1 in enumerate(date_cols):
                for col2 in date_cols[i+1:]:
                    if ('start' in col1.lower() and 'end' in col2.lower()) or \
                       ('begin' in col1.lower() and 'end' in col2.lower()) or \
                       ('from' in col1.lower() and 'to' in col2.lower()):
                        try:
                            dates1 = pd.to_datetime(self.df[col1])
                            dates2 = pd.to_datetime(self.df[col2])
                            invalid = (dates1 > dates2).sum()
                            if invalid > 0:
                                consistency_checks.append({
                                    "type": "date_order_violation",
                                    "columns": [col1, col2],
                                    "violation_count": int(invalid),
                                    "message": f"{invalid} rows where {col1} > {col2}",
                                })
                        except (ValueError, TypeError, pd.errors.ParserError):
                            # Date comparison failed, skip this pair
                            pass
        
        return {
            "checks_performed": len(consistency_checks),
            "issues": consistency_checks,
        }
    
    def _detect_outliers(self) -> dict:
        """Detect statistical outliers in numeric columns."""
        outlier_results = {}
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            clean_data = self.df[col].dropna()
            
            if len(clean_data) < 4:  # Need minimum data points
                continue
            
            # IQR method
            Q1 = clean_data.quantile(0.25)
            Q3 = clean_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_mask = (clean_data < lower_bound) | (clean_data > upper_bound)
            outlier_count = int(outliers_mask.sum())
            
            if outlier_count > 0:
                outlier_values = clean_data[outliers_mask]
                outlier_results[col] = {
                    "method": "IQR",
                    "outlier_count": outlier_count,
                    "outlier_percentage": round(outlier_count / len(clean_data) * 100, 2),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "outlier_values_sample": outlier_values.head(10).tolist(),
                    "statistics": {
                        "mean": float(clean_data.mean()),
                        "std": float(clean_data.std()),
                        "min": float(clean_data.min()),
                        "max": float(clean_data.max()),
                        "Q1": float(Q1),
                        "Q3": float(Q3),
                    },
                }
        
        return {
            "columns_checked": len(numeric_cols),
            "columns_with_outliers": len(outlier_results),
            "column_outliers": outlier_results,
        }
    
    def _calculate_quality_score(self, completeness: dict, uniqueness: dict,
                                 validity: dict, consistency: dict, 
                                 outliers: dict) -> dict:
        """Calculate overall quality score (0-100)."""
        scores = {}
        
        # Completeness score (0-30 points)
        completeness_pct = completeness.get("overall_completeness", 0)
        scores["completeness"] = min(30, completeness_pct * 0.30)
        
        # Uniqueness score (0-20 points) - based on duplicate rows
        dup_pct = uniqueness.get("duplicate_row_percentage", 0)
        scores["uniqueness"] = max(0, 20 - (dup_pct * 0.2))
        
        # Validity score (0-25 points) - based on format issues
        validity_issues = sum(1 for col, info in validity.items() 
                             if info.get("issues"))
        validity_score = max(0, 25 - (validity_issues * 2.5))
        scores["validity"] = validity_score
        
        # Consistency score (0-15 points)
        consistency_issues = len(consistency.get("issues", []))
        scores["consistency"] = max(0, 15 - (consistency_issues * 3))
        
        # Outlier score (0-10 points)
        outlier_cols = outliers.get("columns_with_outliers", 0)
        scores["outliers"] = max(0, 10 - (outlier_cols * 1))
        
        total_score = sum(scores.values())
        
        return {
            "total": round(total_score, 1),
            "grade": self._get_grade(total_score),
            "breakdown": scores,
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_summary(self, completeness: dict, uniqueness: dict,
                         validity: dict, consistency: dict, 
                         outliers: dict) -> dict:
        """Generate human-readable summary."""
        return {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "completeness": f"{completeness.get('overall_completeness', 0)}% complete",
            "duplicates": f"{uniqueness.get('duplicate_row_count', 0)} duplicate rows",
            "empty_columns": len(completeness.get("empty_columns", [])),
            "high_null_columns": len(completeness.get("high_null_columns", [])),
            "potential_id_columns": uniqueness.get("potential_id_columns", []),
            "consistency_issues": len(consistency.get("issues", [])),
            "columns_with_outliers": outliers.get("columns_with_outliers", 0),
        }
    
    def _generate_recommendations(self, completeness: dict, uniqueness: dict,
                                  validity: dict, outliers: dict) -> list:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Completeness recommendations
        if completeness.get("empty_columns"):
            recommendations.append({
                "category": "completeness",
                "priority": "high",
                "message": f"Remove {len(completeness['empty_columns'])} empty column(s)",
                "columns": completeness["empty_columns"],
            })
        
        if completeness.get("high_null_columns"):
            recommendations.append({
                "category": "completeness",
                "priority": "medium",
                "message": f"Review {len(completeness['high_null_columns'])} column(s) with >50% null values",
                "columns": completeness["high_null_columns"],
            })
        
        # Uniqueness recommendations
        if uniqueness.get("duplicate_row_count", 0) > 0:
            recommendations.append({
                "category": "uniqueness",
                "priority": "high",
                "message": f"Investigate {uniqueness['duplicate_row_count']} duplicate rows",
                "action": "Review and potentially deduplicate",
            })
        
        # Validity recommendations
        for col, info in validity.items():
            if info.get("issues"):
                for issue in info["issues"]:
                    if issue.get("type") == "whitespace_issues":
                        recommendations.append({
                            "category": "validity",
                            "priority": "low",
                            "message": f"Clean whitespace in column '{col}'",
                            "column": col,
                        })
        
        # Outlier recommendations
        if outliers.get("columns_with_outliers", 0) > 0:
            recommendations.append({
                "category": "outliers",
                "priority": "medium",
                "message": f"Review outliers in {outliers['columns_with_outliers']} column(s)",
                "columns": list(outliers.get("column_outliers", {}).keys()),
            })
        
        return recommendations


class MultiDatasetQualityChecker:
    """Compare quality metrics across multiple datasets."""
    
    def __init__(self, dataframes: dict[str, pd.DataFrame]):
        """
        Initialize with multiple dataframes.
        
        Args:
            dataframes: Dict mapping name -> DataFrame
        """
        self.dataframes = dataframes
        self.checkers = {
            name: QualityChecker(df, name)
            for name, df in dataframes.items()
        }
    
    def check_all(self) -> dict:
        """Run quality checks on all datasets and compare."""
        individual_results = {}
        for name, checker in self.checkers.items():
            individual_results[name] = checker.check_all()
        
        # Compare quality scores
        comparison = self._compare_quality(individual_results)
        
        return {
            "individual_results": individual_results,
            "comparison": comparison,
            "overall_summary": self._generate_overall_summary(individual_results),
        }
    
    def _compare_quality(self, results: dict) -> dict:
        """Compare quality metrics across datasets."""
        comparison = {
            "scores": {name: res["quality_score"]["total"] 
                      for name, res in results.items()},
            "best_quality": max(results.keys(), 
                               key=lambda k: results[k]["quality_score"]["total"]),
            "completeness_comparison": {
                name: res["completeness"]["overall_completeness"]
                for name, res in results.items()
            },
            "duplicate_comparison": {
                name: res["uniqueness"]["duplicate_row_percentage"]
                for name, res in results.items()
            },
        }
        
        return comparison
    
    def _generate_overall_summary(self, results: dict) -> dict:
        """Generate overall summary across all datasets."""
        total_rows = sum(res["row_count"] for res in results.values())
        avg_score = sum(res["quality_score"]["total"] for res in results.values()) / len(results)
        
        return {
            "dataset_count": len(results),
            "total_rows": total_rows,
            "average_quality_score": round(avg_score, 1),
            "average_grade": QualityChecker(pd.DataFrame(), "temp")._get_grade(avg_score),
        }

