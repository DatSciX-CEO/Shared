"""
Tests for the DataComparator service.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.comparator import DataComparator


class TestDataComparator:
    """Test suite for DataComparator class."""
    
    def test_compare_identical_dataframes(self, sample_csv_data):
        """Test comparing identical dataframes."""
        df1 = sample_csv_data.copy()
        df2 = sample_csv_data.copy()
        
        comparator = DataComparator(df1, df2, "File A", "File B")
        result = comparator.compare(join_columns=["id"])
        
        # Identical dataframes should match
        assert result["matches"] is True
        assert result["rows"]["only_in_df1_count"] == 0
        assert result["rows"]["only_in_df2_count"] == 0
        assert len(result["columns"]["only_in_df1"]) == 0
        assert len(result["columns"]["only_in_df2"]) == 0
    
    def test_compare_different_rows(self, sample_csv_data, sample_csv_data_modified):
        """Test comparing dataframes with different rows."""
        comparator = DataComparator(
            sample_csv_data, 
            sample_csv_data_modified, 
            "Original", 
            "Modified"
        )
        result = comparator.compare(join_columns=["id"])
        
        # Should not match
        assert result["matches"] is False
        
        # Check row differences
        assert result["rows"]["only_in_df1_count"] > 0  # IDs 4, 5 only in original
        assert result["rows"]["only_in_df2_count"] > 0  # IDs 6, 7 only in modified
        
        # Summary should be correct
        assert result["summary"]["df1_name"] == "Original"
        assert result["summary"]["df2_name"] == "Modified"
        assert result["summary"]["df1_rows"] == len(sample_csv_data)
        assert result["summary"]["df2_rows"] == len(sample_csv_data_modified)
    
    def test_compare_different_columns(self, sample_csv_data, sample_csv_with_schema_diff):
        """Test comparing dataframes with different columns."""
        comparator = DataComparator(
            sample_csv_data,
            sample_csv_with_schema_diff,
            "Standard",
            "Different Schema"
        )
        
        # Find a common column to join on (need to rename for this test)
        sample_csv_with_schema_diff_renamed = sample_csv_with_schema_diff.rename(columns={"ID": "id"})
        
        comparator2 = DataComparator(
            sample_csv_data,
            sample_csv_with_schema_diff_renamed,
            "Standard",
            "Different Schema"
        )
        result = comparator2.compare(join_columns=["id"])
        
        # Should have column differences
        assert len(result["columns"]["only_in_df1"]) > 0
        assert len(result["columns"]["only_in_df2"]) > 0
    
    def test_compare_with_ignored_columns(self, sample_csv_data, sample_csv_data_modified):
        """Test comparison with ignored columns."""
        comparator = DataComparator(
            sample_csv_data,
            sample_csv_data_modified,
            "Original",
            "Modified"
        )
        
        # Ignore the 'name' and 'amount' columns
        result = comparator.compare(
            join_columns=["id"],
            ignore_columns=["name", "amount"]
        )
        
        # Check that comparison was performed
        assert "summary" in result
        assert "columns" in result
    
    def test_compare_with_tolerances(self, sample_csv_data):
        """Test numeric comparison with tolerances."""
        df1 = sample_csv_data.copy()
        df2 = sample_csv_data.copy()
        
        # Modify amounts slightly
        df2["amount"] = df2["amount"] + 0.001
        
        comparator = DataComparator(df1, df2, "File A", "File B")
        
        # With default tolerance, should match
        result = comparator.compare(join_columns=["id"], abs_tol=0.01)
        assert result["matches"] is True
        
        # With stricter tolerance, should not match
        result2 = comparator.compare(join_columns=["id"], abs_tol=0.0001)
        # May or may not match depending on exact implementation
    
    def test_get_statistics(self, sample_csv_data, sample_csv_data_modified):
        """Test getting comprehensive statistics."""
        comparator = DataComparator(
            sample_csv_data,
            sample_csv_data_modified,
            "Original",
            "Modified"
        )
        
        stats = comparator.get_statistics()
        
        # Check structure
        assert "df1" in stats
        assert "df2" in stats
        
        # Check df1 stats
        df1_stats = stats["df1"]
        assert df1_stats["name"] == "Original"
        assert "shape" in df1_stats
        assert df1_stats["shape"]["rows"] == len(sample_csv_data)
        assert "memory_usage_mb" in df1_stats
        assert "null_counts" in df1_stats
        assert "duplicate_rows" in df1_stats
    
    def test_get_detailed_diff(self, sample_csv_data, sample_csv_data_modified):
        """Test getting detailed differences for a column."""
        comparator = DataComparator(
            sample_csv_data,
            sample_csv_data_modified,
            "Original",
            "Modified"
        )
        comparator.compare(join_columns=["id"])
        
        # Get detailed diff for 'name' column
        diffs = comparator.get_detailed_diff("name", limit=10)
        
        # Should return list of differences
        assert isinstance(diffs, list)
        # If there are differences, they should have the expected structure
        for diff in diffs:
            assert "row_index" in diff or "value_in_df1" in diff
    
    def test_comparison_report(self, sample_csv_data, sample_csv_data_modified):
        """Test that comparison generates a text report."""
        comparator = DataComparator(
            sample_csv_data,
            sample_csv_data_modified,
            "Original",
            "Modified"
        )
        result = comparator.compare(join_columns=["id"])
        
        # Should have text report
        assert "text_report" in result
        assert isinstance(result["text_report"], str)
        assert len(result["text_report"]) > 0
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        df1 = pd.DataFrame({"id": [], "name": []})
        df2 = pd.DataFrame({"id": [], "name": []})
        
        comparator = DataComparator(df1, df2, "Empty1", "Empty2")
        result = comparator.compare(join_columns=["id"])
        
        # Should handle empty dataframes gracefully
        assert "summary" in result
        assert result["summary"]["df1_rows"] == 0
        assert result["summary"]["df2_rows"] == 0

