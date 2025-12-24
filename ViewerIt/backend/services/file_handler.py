"""
File Handler Service - Handles file uploads and format detection for eDiscovery data.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
import pandas as pd

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


class FileHandler:
    """Handles file operations for data comparison."""
    
    SUPPORTED_FORMATS = {
        ".csv": "CSV",
        ".xlsx": "Excel",
        ".xls": "Excel (Legacy)",
        ".parquet": "Parquet",
        ".json": "JSON",
        ".dat": "DAT (Concordance)",
        ".txt": "Text/Delimited",
    }
    
    @classmethod
    def save_uploaded_file(cls, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return the session ID."""
        session_id = str(uuid.uuid4())
        session_dir = UPLOADS_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        file_path = session_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return session_id
    
    @classmethod
    def load_dataframe(cls, session_id: str, filename: str) -> pd.DataFrame:
        """Load a file as a pandas DataFrame."""
        file_path = UPLOADS_DIR / session_id / filename
        ext = Path(filename).suffix.lower()
        
        if ext == ".csv":
            return pd.read_csv(file_path, encoding="utf-8", low_memory=False)
        elif ext in (".xlsx", ".xls"):
            return pd.read_excel(file_path)
        elif ext == ".parquet":
            return pd.read_parquet(file_path)
        elif ext == ".json":
            return pd.read_json(file_path)
        elif ext in (".dat", ".txt"):
            # Try common eDiscovery delimiters
            for delimiter in ["\x14", "|", "\t", ","]:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter, encoding="utf-8")
                    if len(df.columns) > 1:
                        return df
                except Exception:
                    continue
            return pd.read_csv(file_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @classmethod
    def get_file_info(cls, session_id: str, filename: str) -> dict:
        """Get metadata about an uploaded file."""
        file_path = UPLOADS_DIR / session_id / filename
        df = cls.load_dataframe(session_id, filename)
        
        return {
            "filename": filename,
            "session_id": session_id,
            "file_size": file_path.stat().st_size,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        }
    
    @classmethod
    def cleanup_session(cls, session_id: str) -> bool:
        """Remove all files for a session."""
        session_dir = UPLOADS_DIR / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
            return True
        return False
    
    @classmethod
    def get_session_files(cls, session_id: str) -> list[str]:
        """List all files in a session."""
        session_dir = UPLOADS_DIR / session_id
        if session_dir.exists():
            return [f.name for f in session_dir.iterdir() if f.is_file()]
        return []

