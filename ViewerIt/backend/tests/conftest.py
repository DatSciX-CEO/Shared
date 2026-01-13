"""
Pytest configuration and fixtures for ViewerIt backend tests.
"""
import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import json


@pytest.fixture
def temp_upload_dir(tmp_path):
    """Create a temporary upload directory for tests."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    yield upload_dir
    # Cleanup is automatic with tmp_path


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "amount": [100.50, 200.75, 150.25, 300.00, 175.50],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "category": ["A", "B", "A", "C", "B"],
    })


@pytest.fixture
def sample_csv_data_modified():
    """Modified sample data with some differences."""
    return pd.DataFrame({
        "id": [1, 2, 3, 6, 7],  # Different IDs: 4,5 removed, 6,7 added
        "name": ["Alice", "Bobby", "Charlie", "Frank", "Grace"],  # Bob -> Bobby
        "amount": [100.50, 250.00, 150.25, 400.00, 225.50],  # Different amounts
        "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-06", "2024-01-07"],
        "category": ["A", "B", "A", "D", "C"],
    })


@pytest.fixture
def sample_csv_data_third():
    """Third sample data for multi-file comparison."""
    return pd.DataFrame({
        "id": [1, 3, 5, 6, 8],  # Mix of IDs from both
        "name": ["Alice", "Charlie", "Eve", "Frank", "Henry"],
        "amount": [100.50, 150.25, 175.50, 400.00, 500.00],
        "date": ["2024-01-01", "2024-01-03", "2024-01-05", "2024-01-06", "2024-01-08"],
        "category": ["A", "A", "B", "D", "E"],
    })


@pytest.fixture
def sample_csv_with_nulls():
    """Sample data with null values for quality testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", None, "Charlie", "Diana", None],
        "amount": [100.50, 200.75, None, 300.00, 175.50],
        "date": ["2024-01-01", "2024-01-02", "2024-01-03", None, "2024-01-05"],
        "category": ["A", "B", "A", None, "B"],
    })


@pytest.fixture
def sample_csv_with_schema_diff():
    """Sample data with different schema/column names."""
    return pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],  # Different case
        "full_name": ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Ross", "Eve Wilson"],  # Different name
        "total_amount": [100.50, 200.75, 150.25, 300.00, 175.50],  # Different name
        "transaction_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "type": ["A", "B", "A", "C", "B"],  # Different name for category
        "extra_column": ["x", "y", "z", "w", "v"],  # Extra column
    })


@pytest.fixture
def create_temp_csv(temp_upload_dir):
    """Factory fixture to create temporary CSV files."""
    def _create_csv(df: pd.DataFrame, filename: str, session_id: str = "test_session"):
        session_dir = temp_upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        file_path = session_dir / filename
        df.to_csv(file_path, index=False)
        return str(file_path), session_id
    return _create_csv


@pytest.fixture
def create_temp_excel(temp_upload_dir):
    """Factory fixture to create temporary Excel files."""
    def _create_excel(df: pd.DataFrame, filename: str, session_id: str = "test_session"):
        session_dir = temp_upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        file_path = session_dir / filename
        df.to_excel(file_path, index=False)
        return str(file_path), session_id
    return _create_excel


@pytest.fixture
def create_temp_json(temp_upload_dir):
    """Factory fixture to create temporary JSON files."""
    def _create_json(df: pd.DataFrame, filename: str, session_id: str = "test_session"):
        session_dir = temp_upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        file_path = session_dir / filename
        df.to_json(file_path, orient="records")
        return str(file_path), session_id
    return _create_json


@pytest.fixture
def create_temp_parquet(temp_upload_dir):
    """Factory fixture to create temporary Parquet files."""
    def _create_parquet(df: pd.DataFrame, filename: str, session_id: str = "test_session"):
        session_dir = temp_upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        file_path = session_dir / filename
        df.to_parquet(file_path, index=False)
        return str(file_path), session_id
    return _create_parquet

