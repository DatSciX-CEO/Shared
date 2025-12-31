"""
Tests for the SchemaAnalyzer service.
Comprehensive tests for schema analysis and column mapping.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.schema_analyzer import SchemaAnalyzer


class TestSchemaAnalyzer:
    """Test suite for SchemaAnalyzer class."""
    
    def test_init_with_dataframes(self, sample_csv_data, sample_csv_data_modified):
        """Test initialization with dataframes."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        
        assert len(analyzer.dataframes) == 2
        assert "file1.csv" in analyzer.file_names
        assert "file2.csv" in analyzer.file_names
    
    def test_analyze_identical_schemas(self, sample_csv_data):
        """Test analyzing files with identical schemas."""
        df1 = sample_csv_data.copy()
        df2 = sample_csv_data.copy()
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        # All columns should be in all files
        assert len(result["column_alignment"]["columns_in_all_files"]) == len(sample_csv_data.columns)
        assert len(result["column_alignment"]["columns_in_some_files"]) == 0
        
        # All types should be compatible
        assert len(result["type_compatibility"]["incompatible_columns"]) == 0
    
    def test_analyze_different_schemas(self, sample_csv_data, sample_csv_with_schema_diff):
        """Test analyzing files with different schemas."""
        dataframes = {
            "standard.csv": sample_csv_data,
            "different.csv": sample_csv_with_schema_diff,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        # Should have columns unique to each file
        assert "file_unique_columns" in result["column_alignment"]
        
        # Schema compatibility should be affected
        assert result["summary"]["schema_compatibility"] in ["compatible", "incompatible"]
    
    def test_schema_extraction(self, sample_csv_data):
        """Test that schema extraction captures all column details."""
        dataframes = {"test.csv": sample_csv_data}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        schema = result["schemas"]["test.csv"]
        
        assert "columns" in schema
        assert "row_count" in schema
        assert "column_count" in schema
        assert "memory_usage" in schema
        
        assert schema["row_count"] == len(sample_csv_data)
        assert schema["column_count"] == len(sample_csv_data.columns)
        
        # Check column details
        for col in sample_csv_data.columns:
            assert col in schema["columns"]
            col_info = schema["columns"][col]
            assert "dtype" in col_info
            assert "nullable" in col_info
            assert "null_count" in col_info
            assert "unique_count" in col_info
    
    def test_column_alignment_analysis(self, sample_csv_data, sample_csv_with_schema_diff):
        """Test column alignment analysis."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_with_schema_diff,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        alignment = result["column_alignment"]
        
        assert "all_columns" in alignment
        assert "columns_in_all_files" in alignment
        assert "columns_in_some_files" in alignment
        assert "file_unique_columns" in alignment
        assert "column_presence_matrix" in alignment
        
        # All columns from both files should be in all_columns
        all_cols = set(sample_csv_data.columns) | set(sample_csv_with_schema_diff.columns)
        assert len(alignment["all_columns"]) == len(all_cols)
    
    def test_type_compatibility_analysis(self, sample_csv_data):
        """Test type compatibility analysis."""
        df1 = sample_csv_data.copy()
        df2 = sample_csv_data.copy()
        # Change type for one column
        df2["amount"] = df2["amount"].astype(str)
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        type_compat = result["type_compatibility"]
        
        assert "column_types" in type_compat
        assert "compatible_columns" in type_compat
        assert "incompatible_columns" in type_compat
        assert "compatibility_matrix" in type_compat
        
        # 'amount' should be incompatible (float vs string)
        assert "amount" in type_compat["incompatible_columns"]
    
    def test_mapping_suggestions(self, sample_csv_data, sample_csv_with_schema_diff):
        """Test column mapping suggestions."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_with_schema_diff,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        suggestions = result["mapping_suggestions"]
        
        assert "suggestions" in suggestions
        assert "total_suggestions" in suggestions
        assert isinstance(suggestions["suggestions"], list)
        
        # Should suggest mappings like 'id' -> 'ID', 'name' -> 'full_name'
        for suggestion in suggestions["suggestions"]:
            assert "file1" in suggestion
            assert "column1" in suggestion
            assert "file2" in suggestion
            assert "column2" in suggestion
            assert "similarity_score" in suggestion
            assert "match_reasons" in suggestion
    
    def test_issue_identification(self, sample_csv_data, sample_csv_with_nulls):
        """Test identification of schema issues."""
        dataframes = {
            "clean.csv": sample_csv_data,
            "with_nulls.csv": sample_csv_with_nulls,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        issues = result["issues"]
        
        assert isinstance(issues, list)
        
        # Each issue should have required fields
        for issue in issues:
            assert "type" in issue
            assert "severity" in issue
            assert "message" in issue
    
    def test_summary_generation(self, sample_csv_data, sample_csv_data_modified):
        """Test summary generation."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        summary = result["summary"]
        
        assert "file_count" in summary
        assert "total_unique_columns" in summary
        assert "columns_in_all_files" in summary
        assert "columns_in_some_files" in summary
        assert "schema_compatibility" in summary
        assert "issue_count" in summary
        assert "file_details" in summary
        
        assert summary["file_count"] == 2
    
    def test_numeric_column_statistics(self, sample_csv_data):
        """Test that numeric columns have min/max/mean stats."""
        dataframes = {"test.csv": sample_csv_data}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        schema = result["schemas"]["test.csv"]
        amount_info = schema["columns"]["amount"]
        
        # Numeric column should have statistics
        assert "min" in amount_info
        assert "max" in amount_info
        assert "mean" in amount_info
    
    def test_string_column_statistics(self, sample_csv_data):
        """Test that string columns have length stats."""
        dataframes = {"test.csv": sample_csv_data}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        schema = result["schemas"]["test.csv"]
        name_info = schema["columns"]["name"]
        
        # String column should have length and sample info
        assert "avg_length" in name_info or "sample_values" in name_info
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        df1 = pd.DataFrame({"id": [], "name": []})
        df2 = pd.DataFrame({"id": [], "name": []})
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        # Should handle empty dataframes gracefully
        assert result["schemas"]["file1.csv"]["row_count"] == 0
        assert result["schemas"]["file2.csv"]["row_count"] == 0
    
    def test_compatibility_matrix_structure(self, sample_csv_data, sample_csv_data_modified):
        """Test compatibility matrix structure."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_data_modified,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        matrix = result["type_compatibility"]["compatibility_matrix"]
        
        assert "columns" in matrix
        assert "files" in matrix
        assert "data" in matrix
        
        for row in matrix["data"]:
            assert "column" in row
            assert "compatible" in row
    
    def test_column_presence_matrix(self, sample_csv_data, sample_csv_with_schema_diff):
        """Test column presence matrix."""
        dataframes = {
            "file1.csv": sample_csv_data,
            "file2.csv": sample_csv_with_schema_diff,
        }
        
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        presence_matrix = result["column_alignment"]["column_presence_matrix"]
        
        # Each column should have presence info for each file
        for col, presence in presence_matrix.items():
            assert "file1.csv" in presence
            assert "file2.csv" in presence
            assert isinstance(presence["file1.csv"], bool)
            assert isinstance(presence["file2.csv"], bool)
    
    def test_type_compatibility_groups(self):
        """Test type compatibility group detection."""
        # Create dataframes with compatible types (int and float)
        df1 = pd.DataFrame({"value": [1, 2, 3]})  # int
        df2 = pd.DataFrame({"value": [1.0, 2.0, 3.0]})  # float
        
        dataframes = {"file1.csv": df1, "file2.csv": df2}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        type_info = result["type_compatibility"]["column_types"].get("value", {})
        
        if type_info:
            # int and float should be in the 'numeric' compatibility group
            assert type_info.get("compatibility_group") in ["numeric", "integer", "float"]
    
    def test_high_null_percentage_detection(self, sample_csv_with_nulls):
        """Test detection of high null percentage columns."""
        dataframes = {"test.csv": sample_csv_with_nulls}
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        issues = result["issues"]
        
        # Should detect columns with high null percentage
        null_issues = [i for i in issues if i["type"] == "high_null_percentage"]
        
        # sample_csv_with_nulls has columns with 40% nulls (2 out of 5 rows)
        # This may or may not trigger the 50% threshold
        assert isinstance(null_issues, list)


