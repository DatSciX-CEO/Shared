"""
Tests for the FileHandler service.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.file_handler import FileHandler, UPLOADS_DIR, MAX_FILE_SIZE


class TestFileHandler:
    """Test suite for FileHandler class."""
    
    def test_supported_formats(self):
        """Test that all expected formats are supported."""
        expected_formats = [".csv", ".xlsx", ".xls", ".parquet", ".json", ".dat", ".txt"]
        for fmt in expected_formats:
            assert fmt in FileHandler.SUPPORTED_FORMATS
    
    def test_save_uploaded_file(self, tmp_path, sample_csv_data):
        """Test saving an uploaded file."""
        # Create CSV content
        csv_content = sample_csv_data.to_csv(index=False).encode('utf-8')
        
        # Save the file
        session_id = FileHandler.save_uploaded_file(csv_content, "test.csv")
        
        # Verify
        assert session_id is not None
        assert len(session_id) == 36  # UUID format
        
        # Check file exists
        file_path = UPLOADS_DIR / session_id / "test.csv"
        assert file_path.exists()
        
        # Cleanup
        import shutil
        shutil.rmtree(UPLOADS_DIR / session_id)
    
    def test_load_csv_dataframe(self, sample_csv_data):
        """Test loading a CSV file as DataFrame."""
        # Save test file
        csv_content = sample_csv_data.to_csv(index=False).encode('utf-8')
        session_id = FileHandler.save_uploaded_file(csv_content, "test.csv")
        
        try:
            # Load the file
            df = FileHandler.load_dataframe(session_id, "test.csv")
            
            # Verify
            assert isinstance(df, pd.DataFrame)
            assert len(df) == len(sample_csv_data)
            assert list(df.columns) == list(sample_csv_data.columns)
        finally:
            # Cleanup
            FileHandler.cleanup_session(session_id)
    
    def test_load_json_dataframe(self, sample_csv_data):
        """Test loading a JSON file as DataFrame."""
        # Save test file
        json_content = sample_csv_data.to_json(orient='records').encode('utf-8')
        session_id = FileHandler.save_uploaded_file(json_content, "test.json")
        
        try:
            # Load the file
            df = FileHandler.load_dataframe(session_id, "test.json")
            
            # Verify
            assert isinstance(df, pd.DataFrame)
            assert len(df) == len(sample_csv_data)
        finally:
            # Cleanup
            FileHandler.cleanup_session(session_id)
    
    def test_get_file_info(self, sample_csv_data):
        """Test getting file metadata."""
        # Save test file
        csv_content = sample_csv_data.to_csv(index=False).encode('utf-8')
        session_id = FileHandler.save_uploaded_file(csv_content, "test.csv")
        
        try:
            # Get file info
            info = FileHandler.get_file_info(session_id, "test.csv")
            
            # Verify
            assert info["filename"] == "test.csv"
            assert info["session_id"] == session_id
            assert info["rows"] == len(sample_csv_data)
            assert info["columns"] == len(sample_csv_data.columns)
            assert "column_names" in info
            assert "dtypes" in info
        finally:
            # Cleanup
            FileHandler.cleanup_session(session_id)
    
    def test_get_session_files(self, sample_csv_data):
        """Test listing files in a session."""
        # Save multiple test files
        csv_content = sample_csv_data.to_csv(index=False).encode('utf-8')
        session_id = FileHandler.save_uploaded_file(csv_content, "test1.csv")
        
        # Save another file to same session
        session_dir = UPLOADS_DIR / session_id
        (session_dir / "test2.csv").write_bytes(csv_content)
        
        try:
            # Get session files
            files = FileHandler.get_session_files(session_id)
            
            # Verify
            assert len(files) == 2
            assert "test1.csv" in files
            assert "test2.csv" in files
        finally:
            # Cleanup
            FileHandler.cleanup_session(session_id)
    
    def test_cleanup_session(self, sample_csv_data):
        """Test session cleanup."""
        # Save test file
        csv_content = sample_csv_data.to_csv(index=False).encode('utf-8')
        session_id = FileHandler.save_uploaded_file(csv_content, "test.csv")
        
        # Verify file exists
        session_dir = UPLOADS_DIR / session_id
        assert session_dir.exists()
        
        # Cleanup
        result = FileHandler.cleanup_session(session_id)
        
        # Verify
        assert result is True
        assert not session_dir.exists()
    
    def test_cleanup_nonexistent_session(self):
        """Test cleanup of non-existent session returns False."""
        result = FileHandler.cleanup_session("nonexistent-session-id")
        assert result is False
    
    def test_unsupported_format(self):
        """Test that unsupported formats raise an error."""
        content = b"some binary content"
        session_id = FileHandler.save_uploaded_file(content, "test.xyz")
        
        try:
            with pytest.raises(ValueError) as excinfo:
                FileHandler.load_dataframe(session_id, "test.xyz")
            assert "Unsupported file format" in str(excinfo.value)
        finally:
            FileHandler.cleanup_session(session_id)

