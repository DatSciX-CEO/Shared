"""
Tests for the MultiFileComparator service.
Comprehensive tests for multi-file comparison logic.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.multi_comparator import MultiFileComparator


class TestMultiFileComparator:
    """Test suite for MultiFileComparator class."""
    
    def test_init_with_minimum_files(self, sample_csv_data, sample_csv_data_modified):
        """Test initialization with minimum required files (2)."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        
        assert len(comparator.dataframes) == 2
        assert "file1.csv" in comparator.file_names
        assert "file2.csv" in comparator.file_names
    
    def test_init_with_three_files(self, sample_csv_data, sample_csv_data_modified, sample_csv_data_third):
        """Test initialization with three files."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
            "file3.csv": sample_csv_data_third,
        }
        
        comparator = MultiFileComparator(dataframes)
        
        assert len(comparator.dataframes) == 3
    
    def test_init_fails_with_single_file(self, sample_csv_data):
        """Test that initialization fails with only one file."""
        dataframes = {"file1.csv": sample_csv_data}
        
        with pytest.raises(ValueError) as excinfo:
            MultiFileComparator(dataframes)
        
        assert "At least 2 dataframes required" in str(excinfo.value)
    
    def test_compare_identical_files(self, sample_csv_data):
        """Test comparing identical files."""
        df1 = sample_csv_data.copy()
        df2 = sample_csv_data.copy()
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        # All records should be in all files
        assert result["summary"]["records_in_all_files"] == len(sample_csv_data)
        assert result["summary"]["records_in_single_file"] == 0
        assert result["records_in_all_files"]["count"] == len(sample_csv_data)
    
    def test_compare_different_files(self, sample_csv_data, sample_csv_data_modified):
        """Test comparing files with different records."""
        dataframes = {
            "original.csv": sample_csv_data,
            "modified.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        # Check structure
        assert "summary" in result
        assert "records_in_all_files" in result
        assert "records_in_some_files" in result
        assert "records_in_one_file" in result
        assert "presence_matrix" in result
        assert "value_differences" in result
        assert "column_analysis" in result
        
        # IDs 1, 2, 3 are common; 4, 5 only in original; 6, 7 only in modified
        assert result["summary"]["records_in_all_files"] == 3  # Common IDs
        assert result["summary"]["records_in_single_file"] > 0  # Unique records exist
    
    def test_compare_three_files(self, sample_csv_data, sample_csv_data_modified, sample_csv_data_third):
        """Test comparing three files simultaneously."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
            "file3.csv": sample_csv_data_third,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        assert result["summary"]["file_count"] == 3
        assert "venn_data" in result
        assert len(result["venn_data"]["file_names"]) == 3
    
    def test_compare_with_ignored_columns(self, sample_csv_data, sample_csv_data_modified):
        """Test comparison with ignored columns."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(
            join_columns=["id"],
            ignore_columns=["name", "amount"]
        )
        
        # Should still produce valid results
        assert "summary" in result
        assert result["summary"]["file_count"] == 2
    
    def test_missing_join_column_raises_error(self, sample_csv_data):
        """Test that missing join column raises appropriate error."""
        df1 = sample_csv_data.copy()
        df2 = sample_csv_data.drop(columns=["id"])
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        comparator = MultiFileComparator(dataframes)
        
        with pytest.raises(ValueError) as excinfo:
            comparator.compare(join_columns=["id"])
        
        assert "missing join columns" in str(excinfo.value).lower()
    
    def test_presence_matrix_structure(self, sample_csv_data, sample_csv_data_modified):
        """Test that presence matrix has correct structure."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        matrix = result["presence_matrix"]
        assert "headers" in matrix
        assert "rows" in matrix
        assert matrix["headers"][0] == "Key"
        assert "file1.csv" in matrix["headers"]
        assert "file2.csv" in matrix["headers"]
    
    def test_value_differences_detection(self, sample_csv_data, sample_csv_data_modified):
        """Test that value differences are properly detected."""
        dataframes = {
            "original.csv": sample_csv_data,
            "modified.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        # Should detect differences in 'name' and 'amount' for common records
        value_diffs = result["value_differences"]
        assert isinstance(value_diffs, dict)
        
        # Bob was changed to Bobby in ID 2
        if "name" in value_diffs:
            assert value_diffs["name"]["mismatch_count"] > 0
    
    def test_column_analysis(self, sample_csv_data, sample_csv_data_modified):
        """Test column analysis across files."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        column_analysis = result["column_analysis"]
        assert "all_columns" in column_analysis
        assert "columns_in_all_files" in column_analysis
        assert "column_types" in column_analysis
        
        # All columns should be present in both files (same schema)
        assert len(column_analysis["columns_in_all_files"]) > 0
    
    def test_venn_data_structure(self, sample_csv_data, sample_csv_data_modified):
        """Test Venn diagram data structure."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        venn_data = result["venn_data"]
        assert "file_names" in venn_data
        assert "sets" in venn_data
        assert isinstance(venn_data["sets"], list)
        
        # Each set should have 'sets' and 'size' keys
        for venn_set in venn_data["sets"]:
            assert "sets" in venn_set
            assert "size" in venn_set
    
    def test_reconciliation_report(self, sample_csv_data, sample_csv_data_modified):
        """Test reconciliation report generation."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        comparator.compare(join_columns=["id"])
        
        report = comparator.get_reconciliation_report()
        
        assert "summary" in report
        assert "recommendations" in report
        assert "action_items" in report
        assert isinstance(report["recommendations"], list)
    
    def test_reconciliation_report_before_compare_raises_error(self, sample_csv_data):
        """Test that getting report before compare raises error."""
        dataframes = {"file1.csv": sample_csv_data, "file2.csv": sample_csv_data.copy()}
        comparator = MultiFileComparator(dataframes)
        
        with pytest.raises(ValueError) as excinfo:
            comparator.get_reconciliation_report()
        
        assert "compare()" in str(excinfo.value).lower()
    
    def test_export_differences(self, sample_csv_data, sample_csv_data_modified):
        """Test exporting differences as DataFrame."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        comparator = MultiFileComparator(dataframes)
        comparator.compare(join_columns=["id"])
        
        diff_df = comparator.export_differences()
        
        assert isinstance(diff_df, pd.DataFrame)
        if len(diff_df) > 0:
            assert "key" in diff_df.columns
            assert "status" in diff_df.columns
            assert "files" in diff_df.columns
    
    def test_empty_dataframes(self):
        """Test handling of empty dataframes."""
        df1 = pd.DataFrame({"id": [], "name": []})
        df2 = pd.DataFrame({"id": [], "name": []})
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        assert result["summary"]["total_unique_records"] == 0
        assert result["summary"]["records_in_all_files"] == 0
    
    def test_summary_statistics(self, sample_csv_data, sample_csv_data_modified, sample_csv_data_third):
        """Test summary statistics accuracy."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
            "file3.csv": sample_csv_data_third,
        }
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(join_columns=["id"])
        
        summary = result["summary"]
        
        # Verify counts are consistent
        total_unique = summary["total_unique_records"]
        in_all = summary["records_in_all_files"]
        in_single = summary["records_in_single_file"]
        
        # Records in all + in some + in single should equal total unique
        assert total_unique >= in_all
        assert total_unique >= in_single
        
        # File record counts should match actual dataframe lengths
        for file_name, df in dataframes.items():
            assert summary["file_record_counts"][file_name] == len(df)


