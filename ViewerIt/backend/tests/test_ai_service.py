"""
Tests for the AIService.
"""
import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_service import AIService


class TestAIService:
    """Test suite for AIService class."""
    
    def test_get_available_models_returns_list(self):
        """Test that get_available_models returns a list."""
        response = AIService.get_available_models()
        
        assert isinstance(response, dict)
        assert "models" in response
        assert isinstance(response["models"], list)
    
    def test_model_structure(self):
        """Test that returned models have expected structure."""
        response = AIService.get_available_models()
        models = response.get("models", [])
        
        if models:
            for model in models:
                assert "name" in model
                assert isinstance(model["name"], str)
    
    def test_default_models_fallback(self):
        """Test that default models are available."""
        default_models = AIService.DEFAULT_MODELS
        
        assert len(default_models) > 0
        assert "llama3.2" in default_models or "mistral" in default_models
    
    def test_format_comparison_context(self):
        """Test formatting comparison context for AI."""
        sample_summary = {
            "summary": {
                "df1_name": "File A",
                "df2_name": "File B",
                "df1_rows": 100,
                "df2_rows": 95,
                "df1_columns": 10,
                "df2_columns": 10,
                "common_rows": 90,
            },
            "columns": {
                "only_in_df1": ["extra_col"],
                "only_in_df2": [],
                "mismatched": ["amount", "date"],
            },
            "rows": {
                "only_in_df1_count": 10,
                "only_in_df2_count": 5,
            },
            "column_stats": [
                {"column": "amount", "mismatch_count": 15},
                {"column": "date", "mismatch_count": 8},
            ],
        }
        
        context = AIService._format_comparison_context(sample_summary)
        
        # Check that context is properly formatted
        assert isinstance(context, str)
        assert "File A" in context
        assert "File B" in context
        assert "100" in context  # df1_rows
        assert "95" in context   # df2_rows
    
    def test_analyze_comparison_structure(self):
        """Test analyze_comparison returns expected structure."""
        sample_summary = {
            "summary": {
                "df1_name": "Test1",
                "df2_name": "Test2",
                "df1_rows": 10,
                "df2_rows": 10,
            },
            "columns": {"only_in_df1": [], "only_in_df2": [], "mismatched": []},
            "rows": {"only_in_df1_count": 0, "only_in_df2_count": 0},
        }
        
        # This test may fail if Ollama is not running, which is expected
        result = AIService.analyze_comparison(
            model_name="llama3.2",
            comparison_summary=sample_summary,
            user_prompt="Summarize the comparison"
        )
        
        # Should return a dict with success status
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
        assert "model" in result
    
    def test_suggest_join_columns_structure(self):
        """Test suggest_join_columns returns expected structure."""
        df1_cols = ["id", "name", "amount", "date"]
        df2_cols = ["id", "full_name", "total", "created_at"]
        
        # This test may fail if Ollama is not running, which is expected
        result = AIService.suggest_join_columns(
            model_name="llama3.2",
            df1_columns=df1_cols,
            df2_columns=df2_cols
        )
        
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
    
    def test_explain_differences_structure(self):
        """Test explain_differences returns expected structure."""
        differences = [
            {"row_index": 0, "value_in_df1": "Alice", "value_in_df2": "ALICE"},
            {"row_index": 1, "value_in_df1": "Bob", "value_in_df2": "BOB"},
        ]
        
        # This test may fail if Ollama is not running, which is expected
        result = AIService.explain_differences(
            model_name="llama3.2",
            column_name="name",
            differences=differences
        )
        
        assert isinstance(result, dict)
        assert "success" in result or "error" in result

