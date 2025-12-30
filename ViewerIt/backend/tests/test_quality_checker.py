"""
Tests for the QualityChecker service.
Comprehensive tests for data quality analysis.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.quality_checker import QualityChecker, MultiDatasetQualityChecker


class TestQualityChecker:
    """Test suite for QualityChecker class."""
    
    def test_init(self, sample_csv_data):
        """Test initialization."""
        checker = QualityChecker(sample_csv_data, "test_dataset")
        
        assert checker.name == "test_dataset"
        assert len(checker.df) == len(sample_csv_data)
    
    def test_check_all_returns_complete_structure(self, sample_csv_data):
        """Test that check_all returns all expected sections."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        required_keys = [
            "dataset_name",
            "row_count",
            "column_count",
            "quality_score",
            "completeness",
            "uniqueness",
            "validity",
            "consistency",
            "outliers",
            "summary",
            "recommendations",
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_completeness_check_with_no_nulls(self, sample_csv_data):
        """Test completeness check on data without nulls."""
        checker = QualityChecker(sample_csv_data, "clean_data")
        result = checker.check_all()
        
        completeness = result["completeness"]
        
        assert completeness["overall_completeness"] == 100.0
        assert completeness["total_nulls"] == 0
        assert len(completeness["empty_columns"]) == 0
    
    def test_completeness_check_with_nulls(self, sample_csv_with_nulls):
        """Test completeness check on data with nulls."""
        checker = QualityChecker(sample_csv_with_nulls, "null_data")
        result = checker.check_all()
        
        completeness = result["completeness"]
        
        assert completeness["overall_completeness"] < 100.0
        assert completeness["total_nulls"] > 0
        
        # Check column-level completeness
        for col, info in completeness["column_completeness"].items():
            assert "null_count" in info
            assert "null_percentage" in info
            assert "is_complete" in info
    
    def test_uniqueness_check_no_duplicates(self, sample_csv_data):
        """Test uniqueness check on data without duplicates."""
        checker = QualityChecker(sample_csv_data, "unique_data")
        result = checker.check_all()
        
        uniqueness = result["uniqueness"]
        
        assert uniqueness["duplicate_row_count"] == 0
        assert uniqueness["duplicate_row_percentage"] == 0.0
    
    def test_uniqueness_check_with_duplicates(self, sample_csv_data):
        """Test uniqueness check on data with duplicates."""
        # Create data with duplicates
        df_with_dups = pd.concat([sample_csv_data, sample_csv_data.head(2)], ignore_index=True)
        
        checker = QualityChecker(df_with_dups, "dup_data")
        result = checker.check_all()
        
        uniqueness = result["uniqueness"]
        
        assert uniqueness["duplicate_row_count"] > 0
        assert uniqueness["duplicate_row_percentage"] > 0
    
    def test_potential_id_column_detection(self, sample_csv_data):
        """Test detection of potential ID columns."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        uniqueness = result["uniqueness"]
        
        # 'id' column should be detected as potential ID column
        assert "id" in uniqueness["potential_id_columns"]
    
    def test_categorical_column_detection(self, sample_csv_data):
        """Test detection of categorical columns."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        uniqueness = result["uniqueness"]
        
        # 'category' column with low cardinality should be detected
        assert "categorical_columns" in uniqueness
    
    def test_validity_check(self, sample_csv_data):
        """Test validity check."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        validity = result["validity"]
        
        assert isinstance(validity, dict)
        
        for col, info in validity.items():
            assert "dtype" in info
            assert "format_checks" in info
            assert "issues" in info
    
    def test_validity_check_with_email_column(self):
        """Test validity check with email column."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "email": ["test@example.com", "invalid_email", "user@domain.org"],
        })
        
        checker = QualityChecker(df, "email_test")
        result = checker.check_all()
        
        validity = result["validity"]
        email_validity = validity.get("email", {})
        
        # Should have format check results
        assert "format_checks" in email_validity
    
    def test_consistency_check(self, sample_csv_data):
        """Test consistency check."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        consistency = result["consistency"]
        
        assert "checks_performed" in consistency
        assert "issues" in consistency
        assert isinstance(consistency["issues"], list)
    
    def test_consistency_high_correlation_detection(self):
        """Test detection of highly correlated columns."""
        df = pd.DataFrame({
            "value1": [1, 2, 3, 4, 5],
            "value2": [2, 4, 6, 8, 10],  # Perfectly correlated
            "value3": [10, 20, 30, 40, 50],  # Also correlated
        })
        
        checker = QualityChecker(df, "corr_test")
        result = checker.check_all()
        
        consistency = result["consistency"]
        
        # Should detect high correlation
        correlation_issues = [i for i in consistency["issues"] if i["type"] == "high_correlation"]
        assert len(correlation_issues) > 0
    
    def test_outlier_detection(self):
        """Test outlier detection using IQR method."""
        # Create data with outliers
        df = pd.DataFrame({
            "id": list(range(1, 101)),
            "value": [10] * 95 + [1000, 2000, 3000, 4000, 5000],  # 5 outliers
        })
        
        checker = QualityChecker(df, "outlier_test")
        result = checker.check_all()
        
        outliers = result["outliers"]
        
        assert outliers["columns_checked"] > 0
        assert outliers["columns_with_outliers"] > 0
        assert "value" in outliers["column_outliers"]
        
        value_outliers = outliers["column_outliers"]["value"]
        assert value_outliers["outlier_count"] == 5
        assert value_outliers["method"] == "IQR"
    
    def test_outlier_statistics(self):
        """Test that outlier detection includes statistics."""
        df = pd.DataFrame({
            "id": list(range(1, 11)),
            "value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100],  # One outlier
        })
        
        checker = QualityChecker(df, "stats_test")
        result = checker.check_all()
        
        if "value" in result["outliers"]["column_outliers"]:
            stats = result["outliers"]["column_outliers"]["value"]["statistics"]
            
            assert "mean" in stats
            assert "std" in stats
            assert "min" in stats
            assert "max" in stats
            assert "Q1" in stats
            assert "Q3" in stats
    
    def test_quality_score_calculation(self, sample_csv_data):
        """Test quality score calculation."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        quality_score = result["quality_score"]
        
        assert "total" in quality_score
        assert "grade" in quality_score
        assert "breakdown" in quality_score
        
        # Total should be between 0 and 100
        assert 0 <= quality_score["total"] <= 100
        
        # Grade should be A-F
        assert quality_score["grade"] in ["A", "B", "C", "D", "F"]
        
        # Breakdown should have all categories
        breakdown = quality_score["breakdown"]
        assert "completeness" in breakdown
        assert "uniqueness" in breakdown
        assert "validity" in breakdown
        assert "consistency" in breakdown
        assert "outliers" in breakdown
    
    def test_quality_grade_boundaries(self):
        """Test quality grade assignment."""
        checker = QualityChecker(pd.DataFrame(), "test")
        
        assert checker._get_grade(95) == "A"
        assert checker._get_grade(85) == "B"
        assert checker._get_grade(75) == "C"
        assert checker._get_grade(65) == "D"
        assert checker._get_grade(50) == "F"
    
    def test_recommendations_generation(self, sample_csv_with_nulls):
        """Test that recommendations are generated."""
        checker = QualityChecker(sample_csv_with_nulls, "test")
        result = checker.check_all()
        
        recommendations = result["recommendations"]
        
        assert isinstance(recommendations, list)
        
        for rec in recommendations:
            assert "category" in rec
            assert "priority" in rec
            assert "message" in rec
    
    def test_summary_generation(self, sample_csv_data):
        """Test summary generation."""
        checker = QualityChecker(sample_csv_data, "test")
        result = checker.check_all()
        
        summary = result["summary"]
        
        assert "total_rows" in summary
        assert "total_columns" in summary
        assert "completeness" in summary
        assert "duplicates" in summary
    
    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        df = pd.DataFrame({"id": [], "name": []})
        
        checker = QualityChecker(df, "empty")
        result = checker.check_all()
        
        assert result["row_count"] == 0
        assert result["completeness"]["total_cells"] == 0
    
    def test_whitespace_detection(self):
        """Test detection of whitespace issues."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": [" Alice", "Bob ", "  Charlie  "],  # Various whitespace issues
        })
        
        checker = QualityChecker(df, "whitespace_test")
        result = checker.check_all()
        
        validity = result["validity"]
        name_validity = validity.get("name", {})
        
        # Should detect whitespace issues
        issues = name_validity.get("issues", [])
        whitespace_issues = [i for i in issues if i.get("type") == "whitespace_issues"]
        assert len(whitespace_issues) > 0
    
    def test_case_consistency_detection(self):
        """Test detection of case consistency."""
        df = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "status": ["ACTIVE", "ACTIVE", "ACTIVE", "ACTIVE", "active"],  # Mixed case
        })
        
        checker = QualityChecker(df, "case_test")
        result = checker.check_all()
        
        validity = result["validity"]
        status_validity = validity.get("status", {})
        
        # Should have case consistency info
        assert "case_consistency" in status_validity


class TestMultiDatasetQualityChecker:
    """Test suite for MultiDatasetQualityChecker class."""
    
    def test_init(self, sample_csv_data, sample_csv_data_modified):
        """Test initialization with multiple datasets."""
        dataframes = {
            "dataset1": sample_csv_data,
            "dataset2": sample_csv_data_modified,
        }
        
        checker = MultiDatasetQualityChecker(dataframes)
        
        assert len(checker.dataframes) == 2
        assert len(checker.checkers) == 2
    
    def test_check_all_returns_complete_structure(self, sample_csv_data, sample_csv_data_modified):
        """Test that check_all returns all expected sections."""
        dataframes = {
            "dataset1": sample_csv_data,
            "dataset2": sample_csv_data_modified,
        }
        
        checker = MultiDatasetQualityChecker(dataframes)
        result = checker.check_all()
        
        assert "individual_results" in result
        assert "comparison" in result
        assert "overall_summary" in result
    
    def test_individual_results(self, sample_csv_data, sample_csv_data_modified):
        """Test that individual results are included."""
        dataframes = {
            "dataset1": sample_csv_data,
            "dataset2": sample_csv_data_modified,
        }
        
        checker = MultiDatasetQualityChecker(dataframes)
        result = checker.check_all()
        
        individual = result["individual_results"]
        
        assert "dataset1" in individual
        assert "dataset2" in individual
        
        # Each individual result should have full quality check
        for name, res in individual.items():
            assert "quality_score" in res
            assert "completeness" in res
            assert "uniqueness" in res
    
    def test_quality_comparison(self, sample_csv_data, sample_csv_with_nulls):
        """Test quality comparison across datasets."""
        dataframes = {
            "clean": sample_csv_data,
            "with_nulls": sample_csv_with_nulls,
        }
        
        checker = MultiDatasetQualityChecker(dataframes)
        result = checker.check_all()
        
        comparison = result["comparison"]
        
        assert "scores" in comparison
        assert "best_quality" in comparison
        assert "completeness_comparison" in comparison
        assert "duplicate_comparison" in comparison
        
        # Clean dataset should have higher quality
        assert comparison["scores"]["clean"] >= comparison["scores"]["with_nulls"]
        assert comparison["best_quality"] == "clean"
    
    def test_overall_summary(self, sample_csv_data, sample_csv_data_modified):
        """Test overall summary generation."""
        dataframes = {
            "dataset1": sample_csv_data,
            "dataset2": sample_csv_data_modified,
        }
        
        checker = MultiDatasetQualityChecker(dataframes)
        result = checker.check_all()
        
        summary = result["overall_summary"]
        
        assert "dataset_count" in summary
        assert "total_rows" in summary
        assert "average_quality_score" in summary
        assert "average_grade" in summary
        
        assert summary["dataset_count"] == 2
        assert summary["total_rows"] == len(sample_csv_data) + len(sample_csv_data_modified)


